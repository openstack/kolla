#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/etcd" ]]; then
    mkdir -p /var/log/kolla/etcd
fi
if [[ $(stat -c %a /var/log/kolla/etcd) != "755" ]]; then
    chmod 755 /var/log/kolla/etcd
fi

if [[ $(stat -c %U /var/lib/etcd/) != "etcd" ]]; then
    sudo chown etcd: /var/lib/etcd/
fi
