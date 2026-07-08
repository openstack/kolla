#!/bin/bash

if [[ ! -d "/var/log/kolla/hacluster" ]]; then
    mkdir -p /var/log/kolla/hacluster
fi
if [[ $(stat -c %a /var/log/kolla/hacluster) != "755" ]]; then
    chmod 755 /var/log/kolla/hacluster
fi
