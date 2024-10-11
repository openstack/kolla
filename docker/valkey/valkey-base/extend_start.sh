#!/bin/bash

if [[ ! -d "/var/log/kolla/valkey" ]]; then
    mkdir -p /var/log/kolla/valkey
fi

if [[ $(stat -c %a /var/log/kolla/valkey) != "755" ]]; then
    chmod 755 /var/log/kolla/valkey
fi
