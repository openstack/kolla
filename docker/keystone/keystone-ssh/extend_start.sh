#!/bin/bash

if [[ "${KOLLA_BASE_DISTRO}" =~ centos|rocky ]]; then
    # NOTE(mnasiadka): EL10 and CentOS Stream 9 does not support dsa
    SSH_HOST_KEY_TYPES=( "rsa" "ecdsa" "ed25519" )
else
    SSH_HOST_KEY_TYPES=( "rsa" "dsa" "ecdsa" "ed25519" )
fi

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
