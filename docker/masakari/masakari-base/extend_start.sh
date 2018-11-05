#!/bin/bash

if [[ ! -d "/var/log/kolla/masakari" ]]; then
    mkdir -p /var/log/kolla/masakari
fi
if [[ $(stat -c %a /var/log/kolla/masakari) != "755" ]]; then
    chmod 755 /var/log/kolla/masakari
fi

. /usr/local/bin/kolla_masakari_extend_start
