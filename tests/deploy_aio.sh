#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

function print_failure {
    docker ps -a
    for failed in $(docker ps -a --format "{{.Names}}" --filter status=exited); do
        docker logs --tail=all $failed
    done
    echo "FAILED"
    exit 1
}

# Populate globals.yml
cat << EOF > /etc/kolla/globals.yml
---
kolla_base_distro: "$1"
kolla_install_type: "$2"
kolla_internal_address: "169.254.169.10"
docker_pull_policy: "missing"
docker_restart_policy: "no"
network_interface: "eth0"
neutron_external_interface: "fake_interface"
openstack_release: "latest"
EOF

# Create dummy interface for neutron
ip l a fake_interface type dummy

# Actually do the deployment
tools/kolla-ansible deploy || print_failure

# TODO(SamYaple): Actually validate that all containers are started
docker ps -a

# TODO(SamYaple): Actually do functional testing of OpenStack
