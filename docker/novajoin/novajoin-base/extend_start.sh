#!/bin/bash

if [[ ! -d "/var/log/kolla/novajoin" ]]; then
    mkdir -p /var/log/kolla/novajoin
fi
if [[ $(stat -c %a /var/log/kolla/novajoin) != "755" ]]; then
    chmod 755 /var/log/kolla/novajoin
fi

. /usr/local/bin/kolla_novajoin_extend_start
