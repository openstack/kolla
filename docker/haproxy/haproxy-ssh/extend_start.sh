#!/bin/bash

SSH_HOST_KEY_TYPES=( "ecdsa" )

for key_type in ${SSH_HOST_KEY_TYPES[@]}; do
    KEY_PATH=/etc/ssh/ssh_host_${key_type}_key
    if [[ ! -f "${KEY_PATH}" ]]; then
        ssh-keygen -q -t ${key_type} -f ${KEY_PATH} -N ""
    fi
done

mkdir -p /var/lib/haproxy/.ssh

if [[ $(stat -c %U:%G /var/lib/haproxy/.ssh) != "haproxy:haproxy" ]]; then
    sudo chown haproxy: /var/lib/haproxy/.ssh
fi
