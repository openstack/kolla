#!/bin/bash

if [[ ! -d "/var/log/kolla/glance" ]]; then
    mkdir -p /var/log/kolla/glance
fi
if [[ $(stat -c %a /var/log/kolla/glance) != "755" ]]; then
    chmod 755 /var/log/kolla/glance
fi

. /usr/local/bin/kolla_glance_extend_start
