#!/bin/bash

if [[ ! -d "/var/log/kolla/ceph" ]]; then
    mkdir -p /var/log/kolla/ceph
fi
if [[ $(stat -c %a /var/log/kolla/ceph) != "755" ]]; then
    chmod 755 /var/log/kolla/ceph
fi
