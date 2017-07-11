#!/bin/bash

if [[ ! -d "/var/log/kolla/zun" ]]; then
    mkdir -p /var/log/kolla/zun
fi
if [[ $(stat -c %U:%G /var/log/kolla/zun) != "zun:kolla" ]]; then
    chown zun:kolla /var/log/kolla/zun
fi
if [[ $(stat -c %a /var/log/kolla/zun) != "755" ]]; then
    chmod 755 /var/log/kolla/zun
fi

. /usr/local/bin/kolla_zun_extend_start
