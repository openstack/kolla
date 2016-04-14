#!/bin/bash

if [[ ! -d "/var/log/kolla/congress" ]]; then
    mkdir -p /var/log/kolla/congress
fi
if [[ $(stat -c %a /var/log/kolla/congress) != "755" ]]; then
    chmod 755 /var/log/kolla/congress
fi

. /usr/local/bin/kolla_congress_extend_start
