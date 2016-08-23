#!/bin/bash

if [[ ! -d "/var/log/kolla/senlin" ]]; then
    mkdir -p /var/log/kolla/senlin
fi
if [[ $(stat -c %a /var/log/kolla/senlin) != "755" ]]; then
    chmod 755 /var/log/kolla/senlin
fi

. /usr/local/bin/kolla_senlin_extend_start
