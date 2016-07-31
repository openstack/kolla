#!/bin/bash

if [[ ! -d "/var/log/kolla/cloudkitty" ]]; then
    mkdir -p /var/log/kolla/cloudkitty
fi
if [[ $(stat -c %a /var/log/kolla/cloudkitty) != "755" ]]; then
    chmod 755 /var/log/kolla/cloudkitty
fi

. /usr/local/bin/kolla_cloudkitty_extend_start
