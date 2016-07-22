#! /bin/bash

if [[ ! -d "/var/log/kolla/tempest" ]]; then
    mkdir -p /var/log/kolla/tempest
fi
if [[ $(stat -c %a /var/log/kolla/tempest) != "755" ]]; then
    chmod 755 /var/log/kolla/tempest
fi
