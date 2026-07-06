#!/bin/bash

if [[ ! -d "/var/log/kolla/designate" ]]; then
    mkdir -p /var/log/kolla/designate
fi
if [[ $(stat -c %a /var/log/kolla/designate) != "755" ]]; then
    chmod 755 /var/log/kolla/designate
fi

. /usr/local/bin/kolla_designate_extend_start
