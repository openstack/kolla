#!/bin/bash

if [[ ! -d "/var/log/kolla/trove" ]]; then
    mkdir -p /var/log/kolla/trove
fi
if [[ $(stat -c %a /var/log/kolla/trove) != "755" ]]; then
    chmod 755 /var/log/kolla/trove
fi

. /usr/local/bin/kolla_trove_extend_start
