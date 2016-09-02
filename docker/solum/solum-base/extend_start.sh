#!/bin/bash

if [[ ! -d "/var/log/kolla/solum" ]]; then
    mkdir -p /var/log/kolla/solum
fi
if [[ $(stat -c %a /var/log/kolla/solum) != "755" ]]; then
    chmod 755 /var/log/kolla/solum
fi

. /usr/local/bin/kolla_solum_extend_start
