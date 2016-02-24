#!/bin/bash

if [[ ! -d "/var/log/kolla/magnum" ]]; then
    mkdir -p /var/log/kolla/magnum
fi
if [[ $(stat -c %a /var/log/kolla/magnum) != "755" ]]; then
    chmod 755 /var/log/kolla/magnum
fi

source /usr/local/bin/kolla_magnum_extend_start
