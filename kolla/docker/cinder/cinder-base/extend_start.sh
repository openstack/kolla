#!/bin/bash

if [[ ! -d "/var/log/kolla/cinder" ]]; then
    mkdir -p /var/log/kolla/cinder
fi
if [[ $(stat -c %U:%G /var/log/kolla/cinder) != "cinder:kolla" ]]; then
    chown -R cinder:kolla /var/log/kolla/cinder
fi
if [[ $(stat -c %a /var/log/kolla/cinder) != "755" ]]; then
    chmod 755 /var/log/kolla/cinder
fi

. /usr/local/bin/kolla_cinder_extend_start
