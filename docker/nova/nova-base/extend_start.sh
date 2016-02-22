#!/bin/bash

if [[ ! -d "/var/log/kolla/nova" ]]; then
    mkdir -p /var/log/kolla/nova
fi
if [[ $(stat -c %a /var/log/kolla/nova) != "755" ]]; then
    chmod 755 /var/log/kolla/nova
fi

source /usr/local/bin/kolla_nova_extend_start
