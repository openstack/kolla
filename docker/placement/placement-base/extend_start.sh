#!/bin/bash

if [[ ! -d "/var/log/kolla/placement" ]]; then
    mkdir -p /var/log/kolla/placement
    touch /var/log/kolla/placement/placement-api.log
fi
if [[ $(stat -c %U:%G /var/log/kolla/placement) != "placement:kolla" ]]; then
    chown -R placement:kolla /var/log/kolla/placement
fi
if [[ $(stat -c %a /var/log/kolla/placement) != "755" ]]; then
    chmod 755 /var/log/kolla/placement
    chmod 644 /var/log/kolla/placement/placement-api.log
fi

. /usr/local/bin/kolla_placement_extend_start
