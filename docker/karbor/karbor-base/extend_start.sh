#!/bin/bash

if [[ ! -d "/var/log/kolla/karbor" ]]; then
    mkdir -p /var/log/kolla/karbor
fi
if [[ $(stat -c %a /var/log/kolla/karbor) != "755" ]]; then
    chmod 755 /var/log/kolla/karbor
fi

. /usr/local/bin/kolla_karbor_extend_start
