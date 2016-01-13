#!/bin/bash

set -o xtrace
set -o errexit

# Just for mandre :)
if [[ ! -f /etc/sudoers.d/jenkins ]]; then
    echo "jenkins ALL=(:docker) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/jenkins
fi

function dump_node_info {
    # NOTE(SamYaple): function for debugging gate
    set +o errexit
    local OLD_PATH="${PATH}"
    PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    sudo parted -l

    sudo mount

    df -h

    uname -a

    cat /etc/*release*

    PATH="${OLD_PATH}"
    set -o errexit
}

function detect_disk {
    # TODO(SamYaple): This check could be much better, but should work for now
    if [[ $(hostname | grep rax) ]]; then
        export DEV="xvde"
    else
        echo "Assuming this is a hpcloud box"
        export DEV="vdb"
    fi
}

function setup_config {
    # generate the config
    tox -e genconfig
    # Copy configs
    sudo cp -a etc/kolla /etc/
}

function detect_distro {
    DISTRO=$(ansible all -i "localhost," -msetup -clocal | awk -F\" '/ansible_os_family/ {print $4}')
}

function setup_ssh {
    # Generate a new keypair that Ansible will use
    ssh-keygen -f /home/jenkins/.ssh/kolla -N ''
    cat /home/jenkins/.ssh/kolla.pub >> /home/jenkins/.ssh/authorized_keys

    # Push the the public key around to all of the nodes
    for ip in $(cat /etc/nodepool/sub_nodes_private); do
        scp /home/jenkins/.ssh/kolla.pub ${ip}:/home/jenkins/.ssh/authorized_keys
        # TODO(SamYaple): Remove this root key pushing once Kolla doesn't
        # require root anymore.
        ssh ${ip} -i /home/jenkins/.ssh/kolla 'sudo mkdir -p /root/.ssh; sudo cp /home/jenkins/.ssh/* /root/.ssh/'
    done

    # From now on use the new IdentityFile for connecting to other hosts
    echo "IdentityFile /home/jenkins/.ssh/kolla" >> /home/jenkins/.ssh/config
}

function setup_inventory {
    local counter=0

    detect_distro
    if [[ "${DISTRO}" == "Debian" ]]; then
        ANSIBLE_CONNECTION_TYPE=ssh
    else
        ANSIBLE_CONNECTION_TYPE=local
    fi

    echo -e "127.0.0.1\tlocalhost" > /tmp/hosts
    for ip in $(cat /etc/nodepool/{node_private,sub_nodes_private}); do
        : $((counter++))
        echo -e "${ip}\tnode${counter} $(ssh ${ip} hostname)" >> /tmp/hosts
        echo "node${counter} ansible_connection=${ANSIBLE_CONNECTION_TYPE}" >> ${RAW_INVENTORY}
    done

    sudo chown root: /tmp/hosts
    sudo chmod 644 /tmp/hosts
    sudo mv /tmp/hosts /etc/hosts
}

function setup_ansible {
    RAW_INVENTORY=/tmp/kolla/raw_inventory
    mkdir /tmp/kolla

    sudo -H pip install "ansible<2" "docker-py>=1.4.0"

    setup_inventory

    # Record the running state of the environment as seen by the setup module
    ansible all -i ${RAW_INVENTORY} -m setup > /tmp/logs/ansible/initial-setup
}

function setup_node {
    detect_disk
    ansible-playbook -i ${RAW_INVENTORY} -edocker_dev=${DEV} tests/setup_nodes.yml
}

function setup_logging {
    # This directory is the directory that is copied with the devstack-logs
    # publisher. It must exist at /home/jenkins/workspace/<job-name>/logs
    mkdir logs

    # For ease of access we symlink that logs directory to a known path
    ln -s $(pwd)/logs /tmp/logs
    mkdir -p /tmp/logs/{ansible,build}
}

setup_logging
(dump_node_info 2>&1) > /tmp/logs/node_info_first
setup_ssh
setup_ansible
setup_node
setup_config
(dump_node_info 2>&1) > /tmp/logs/node_info_last
