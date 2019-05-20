#!/bin/bash

if [[ ! -d "/var/log/kolla/monasca" ]]; then
    mkdir -p /var/log/kolla/monasca
fi
if [[ $(stat -c %a /var/log/kolla/monasca) != "755" ]]; then
    chmod 755 /var/log/kolla/monasca
fi
