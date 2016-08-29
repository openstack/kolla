#!/bin/bash

if [[ ! -d "/var/log/kolla/manila" ]]; then
    mkdir -p /var/log/kolla/manila
fi
if [[ $(stat -c %a /var/log/kolla/manila) != "755" ]]; then
    chmod 755 /var/log/kolla/manila
fi

. /usr/local/bin/kolla_manila_extend_start
