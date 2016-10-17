#!/bin/bash

if [[ ! -d "/var/log/kolla/panko" ]]; then
    mkdir -p /var/log/kolla/panko
fi
if [[ $(stat -c %a /var/log/kolla/panko) != "755" ]]; then
    chmod 755 /var/log/kolla/panko
fi

. /usr/local/bin/kolla_panko_extend_start
