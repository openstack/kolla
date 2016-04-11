#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

export KOLLA_BASE=$1
export KOLLA_TYPE=$2

function copy_logs {
    cp -rnL /var/lib/docker/volumes/kolla_logs/_data/* /tmp/logs/kolla/
    # NOTE(SamYaple): Fix permissions for log extraction in gate

    if [[ -x "$(command -v journalctl)" ]]; then
        journalctl --no-pager -u docker.service > /tmp/logs/kolla/docker.log
    else
        cp /var/log/upstart/docker.log > /tmp/logs/kolla/docker.log
    fi

    chmod -R 777 /tmp/logs/kolla/
}

function sanity_check {
    # Wait for service ready
    sleep 15
    source /etc/kolla/admin-openrc.sh
    nova --debug service-list
    neutron --debug agent-list
    tools/init-runonce
    nova --debug boot --poll --image $(openstack image list | awk '/cirros/ {print $2}') --nic net-id=$(openstack network list | awk '/demo-net/ {print $2}') --flavor 1 kolla_boot_test
    nova --debug list
    # If the status is not ACTIVE, print info and exit 1
    nova --debug show kolla_boot_test | awk '{buf=buf"\n"$0} $2=="status" && $4!="ACTIVE" {failed="yes"}; END {if (failed=="yes") {print buf; exit 1}}'
}

function check_failure {
    # Command failures after this point can be expected
    set +o errexit

    docker ps -a
    failed_containers=$(docker ps -a --format "{{.Names}}" --filter status=exited)

    for failed in ${failed_containers}; do
        docker logs --tail all ${failed}
    done

    copy_logs
}

function write_configs {
    mkdir -p /etc/kolla/config

    PRIVATE_ADDRESS=$(cat /etc/nodepool/node_private)
    PRIVATE_INTERFACE=$(ip -4 --oneline address | awk -v pattern=${PRIVATE_ADDRESS} '$0 ~ pattern {print $2}')
    cat << EOF > /etc/kolla/globals.yml
---
kolla_base_distro: "${KOLLA_BASE}"
kolla_install_type: "${KOLLA_TYPE}"
kolla_internal_vip_address: "169.254.169.10"
docker_restart_policy: "never"
network_interface: "${PRIVATE_INTERFACE}"
neutron_external_interface: "fake_interface"
enable_horizon: "no"
enable_heat: "no"
EOF

    mkdir /etc/kolla/config/nova
    cat << EOF > /etc/kolla/config/nova/nova-compute.conf
[libvirt]
virt_type=qemu
EOF

    cat << EOF > /etc/kolla/config/nova.conf
[DEFAULT]
osapi_compute_workers = 1

[conductor]
workers = 1
EOF

    cat << EOF > /etc/kolla/config/glance.conf
[DEFAULT]
workers = 1
EOF

    cat << EOF > /etc/kolla/config/neutron.conf
[DEFAULT]
api_workers = 1
metadata_workers = 1
EOF
}

trap check_failure EXIT

write_configs

# Create dummy interface for neutron
ip l a fake_interface type dummy

# Actually do the deployment
tools/kolla-ansible -vvv deploy
tools/kolla-ansible -vvv post-deploy

# Test OpenStack Environment
sanity_check
