#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

function check_failure {
    docker ps -a
    failed_containers=$(docker ps -a --format "{{.Names}}" --filter status=exited)

    for failed in ${failed_containers}; do
        docker logs --tail all ${failed}
    done

    if [[ -n ${failed_containers} ]]; then
        echo 'FAILED'
        exit 1
    fi
}

# Populate globals.yml
cat << EOF > /etc/kolla/globals.yml
---
kolla_base_distro: "$1"
kolla_install_type: "$2"
kolla_internal_address: "169.254.169.10"
docker_restart_policy: "never"
network_interface: "eth0"
neutron_external_interface: "fake_interface"
EOF

# Create dummy interface for neutron
ip l a fake_interface type dummy

# Actually do the deployment
tools/kolla-ansible -vvv deploy

check_failure

# TODO(SamYaple): Actually do functional testing of OpenStack
