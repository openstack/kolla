#!/bin/bash

if [[ ! -d "/var/log/kolla/blazar" ]]; then
    mkdir -p /var/log/kolla/blazar
fi
if [[ $(stat -c %a /var/log/kolla/blazar) != "755" ]]; then
    chmod 755 /var/log/kolla/blazar
fi

. /usr/local/bin/kolla_blazar_extend_start
