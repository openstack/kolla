#!/bin/bash

if [[ -f /opt/kolla/keystone/keystone.conf ]]; then
    cp /opt/kolla/keystone/keystone.conf /etc/keystone/keystone.conf
    chown keystone: /etc/keystone/keystone.conf
    chmod 0644 /etc/keystone/keystone.conf
fi
