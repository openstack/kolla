#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

function create_keys {
    # Setup ssh key as required
    sudo -H ssh-keygen -f /root/.ssh/id_rsa -N ""
    sudo -H cat /root/.ssh/id_rsa.pub | sudo -H tee /root/.ssh/authorized_keys
}

function install_deps {
    # Install Ansible and docker-py
    sudo -H pip install "ansible<2" docker-py
    pip freeze | egrep "docker|ansible"
}

function copy_configs {
    # Copy configs
    sudo cp -a etc/kolla /etc/
}

create_keys
install_deps
copy_configs

# Link the logs directory into root
mkdir -p logs
sudo ln -s $(pwd)/logs /root/logs
