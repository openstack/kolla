#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

export KOLLA_BASE=$1
export KOLLA_TYPE=$2

function check_failure {
    docker ps -a
    failed_containers=$(docker ps -a --format "{{.Names}}" --filter status=exited)

    for failed in ${failed_containers}; do
        docker logs --tail all ${failed}
    done

    journalctl --no-pager -u docker.service || :
    cat /var/log/upstart/docker.log || :

    if [[ -n ${failed_containers} ]]; then
        echo 'FAILED'
        exit 1
    fi
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

# TODO(SamYaple): Actually do functional testing of OpenStack
