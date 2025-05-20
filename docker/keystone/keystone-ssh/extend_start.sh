#!/bin/bash

# NOTE(mnasiadka): CentOS 10 does not support dsa
SSH_HOST_KEY_TYPES=( "rsa" "ecdsa" "ed25519" )

for key_type in ${SSH_HOST_KEY_TYPES[@]}; do
    KEY_PATH=/etc/ssh/ssh_host_${key_type}_key
    if [[ ! -f "${KEY_PATH}" ]]; then
        ssh-keygen -q -t ${key_type} -f ${KEY_PATH} -N ""
    fi
done

mkdir -p /var/lib/keystone/.ssh

if [[ $(stat -c %U:%G /var/lib/keystone/.ssh) != "keystone:keystone" ]]; then
    sudo chown keystone: /var/lib/keystone/.ssh
fi
