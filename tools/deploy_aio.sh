#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

export KOLLA_BASE=$1
export KOLLA_TYPE=$2

function copy_logs {
    docker cp rsyslog:/var/log/ /tmp/logs
}

function check_failure {
    # Command failures after this point can be expected
    set +o errexit

    docker ps -a
    failed_containers=$(docker ps -a --format "{{.Names}}" --filter status=exited)

    for failed in ${failed_containers}; do
        docker logs --tail all ${failed}
    done

    journalctl --no-pager -u docker.service
    cat /var/log/upstart/docker.log

    nova service-list
    neutron agent-list

    nova list
    nova list | awk '/4/ {print $2}' | xargs -n1 nova show

    # NOTE(SamYaple): The copy logs functions is put on hold until Heka is all
    # merged in. At that point we will pull the logs from Heka's volume
    #copy_logs
}

function write_configs {
    mkdir -p /etc/kolla/config

    cat << EOF > /etc/kolla/globals.yml
---
kolla_base_distro: "${KOLLA_BASE}"
kolla_install_type: "${KOLLA_TYPE}"
kolla_internal_address: "169.254.169.10"
docker_restart_policy: "never"
network_interface: "eth0"
neutron_external_interface: "fake_interface"
enable_horizon: "no"
enable_heat: "no"
EOF

    cat << EOF > /etc/kolla/config/nova-compute.conf
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
source /etc/kolla/admin-openrc.sh
tools/init-runonce
# Wait for service ready
sleep 15
nova boot --poll --image $(openstack image list | awk '/cirros/ {print $2}') --nic net-id=$(openstack network list | awk '/demo-net/ {print $2}') --flavor 1 kolla_boot_test

# If the status is not ACTIVE, print info and exit 1
nova show kolla_boot_test | awk '{buf=buf"\n"$0} $2=="status" && $4!="ACTIVE" {failed="yes"}; END {if (failed=="yes") {print buf; exit 1}}'
