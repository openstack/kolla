#!/bin/bash

if [[ ! -d "/var/log/kolla/sahara" ]]; then
    mkdir -p /var/log/kolla/sahara
fi
if [[ $(stat -c %a /var/log/kolla/sahara) != "755" ]]; then
    chmod 755 /var/log/kolla/sahara
fi

. /usr/local/bin/kolla_sahara_extend_start
