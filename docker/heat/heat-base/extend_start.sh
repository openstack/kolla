#!/bin/bash

if [[ ! -d "/var/log/kolla/heat" ]]; then
    mkdir -p /var/log/kolla/heat
fi
if [[ $(stat -c %U:%G /var/log/kolla/heat) != "heat:kolla" ]]; then
    chown -R heat:kolla /var/log/kolla/heat
fi
if [[ $(stat -c %a /var/log/kolla/heat) != "755" ]]; then
    chmod 755 /var/log/kolla/heat
fi

. /usr/local/bin/kolla_heat_extend_start
