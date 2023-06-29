#!/bin/bash

SSH_HOST_KEY_TYPES=( "rsa" "dsa" "ecdsa" "ed25519" )

for key_type in ${SSH_HOST_KEY_TYPES[@]}; do
    KEY_PATH=/etc/ssh/ssh_host_${key_type}_key
    if [[ ! -f "${KEY_PATH}" ]]; then
        ssh-keygen -q -t ${key_type} -f ${KEY_PATH} -N ""
    fi
done

mkdir -p /var/lib/haproxy/.ssh

if [[ $(stat -c %U:%G /var/lib/haproxy/.ssh) != "haproxy:haproxy" ]]; then
    chown haproxy: /var/lib/haproxy/.ssh
fi

FOLDERS_LEGO="/etc/letsencrypt /etc/letsencrypt/backups"
USERGROUP="haproxy:haproxy"

for folder in ${FOLDERS_LEGO}; do
    mkdir -p ${folder}

    if [[ $(stat -c %U:%G ${folder}) != "${USERGROUP}" ]]; then
        chown ${USERGROUP} ${folder}
    fi

    if [[ "${folder}" == "/etc/letsencrypt" ]]; then
        if [[ $(stat -c %a ${folder}) != "751" ]]; then
            chmod 751 ${folder}
        fi
    else
        if [[ $(stat -c %a ${folder}) != "755" ]]; then
            chmod 755 ${folder}
        fi
    fi
done
