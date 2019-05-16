#!/bin/bash

if [[ ! -d "/var/log/kolla/qinling" ]]; then
    mkdir -p /var/log/kolla/qinling
fi
if [[ $(stat -c %a /var/log/kolla/qinling) != "755" ]]; then
    chmod 755 /var/log/kolla/qinling
fi

. /usr/local/bin/kolla_qinling_extend_start
