#!/bin/bash

if [[ ! -d "/var/log/kolla/murano" ]]; then
    mkdir -p /var/log/kolla/murano
fi
if [[ $(stat -c %a /var/log/kolla/murano) != "755" ]]; then
    chmod 755 /var/log/kolla/murano
fi

. /usr/local/bin/kolla_murano_extend_start
