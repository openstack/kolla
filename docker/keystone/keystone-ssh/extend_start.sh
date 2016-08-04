#!/bin/bash

if [[ ! -L /dev/log ]]; then
    ln -sf /var/lib/kolla/heka/log /dev/log
fi

SSH_HOST_KEY_TYPES=( "rsa" "dsa" "ecdsa" "ed25519" )

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
