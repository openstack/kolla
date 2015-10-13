#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

function print_failure {
    docker ps -a
    docker logs bootstrap_keystone
    echo "FAILED"
    exit 1
}

# Setup ssh key as required
ssh-keygen -f kolla-ssh -N ""
cat kolla-ssh.pub | tee /root/.ssh/authorized_keys

# Install Ansible and docker-py
pip install "ansible<2" docker-py
pip freeze | egrep "docker|ansible"

# Setup configs
cp -a etc/kolla /etc/
cat << EOF > /etc/kolla/globals.yml
---
kolla_base_distro: "$1"
kolla_install_type: "$2"
kolla_internal_address: "169.254.169.10"
docker_pull_policy: "missing"
docker_restart_policy: "no"
network_interface: "eth0"
neutron_external_interface: "fake_interface"
EOF

# Create dummy interface for neutron
ip l a fake_interface type dummy

# Actually do the deployment
tools/kolla-ansible deploy || print_failure

# TODO(SamYaple): Actually validate that all containers are started
docker ps -a

# TODO(SamYaple): Actually do functional testing of OpenStack
