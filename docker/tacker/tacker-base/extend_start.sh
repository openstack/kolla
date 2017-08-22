#!/bin/bash

if [[ ! -d "/var/log/kolla/tacker" ]]; then
    mkdir -p /var/log/kolla/tacker
fi
if [[ $(stat -c %a /var/log/kolla/tacker) != "755" ]]; then
    chmod 755 /var/log/kolla/tacker
fi

. /usr/local/bin/kolla_tacker_extend_start
