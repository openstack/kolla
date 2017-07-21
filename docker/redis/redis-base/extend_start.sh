#!/bin/bash

if [[ ! -d "/var/log/kolla/redis" ]]; then
    mkdir -p /var/log/kolla/redis
fi

if [[ $(stat -c %a /var/log/kolla/redis) != "755" ]]; then
    chmod 755 /var/log/kolla/redis
fi
