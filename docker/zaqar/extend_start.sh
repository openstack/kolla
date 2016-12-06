#!/bin/bash

if [[ ! -d "/var/log/kolla/zaqar" ]]; then
    mkdir -p /var/log/kolla/zaqar
fi
if [[ $(stat -c %a /var/log/kolla/zaqar) != "755" ]]; then
    chmod 755 /var/log/kolla/zaqar
fi
