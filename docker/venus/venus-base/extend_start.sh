#!/bin/bash

if [[ ! -d "/var/log/kolla/venus" ]]; then
    mkdir -p /var/log/kolla/venus
fi
if [[ $(stat -c %a /var/log/kolla/venus) != "755" ]]; then
    chmod 755 /var/log/kolla/venus
fi

. /usr/local/bin/kolla_venus_extend_start
