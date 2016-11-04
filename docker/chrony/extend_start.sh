#!/bin/bash

rm -f /var/run/chronyd.pid

if [[ ! -d "/var/log/kolla/chrony" ]]; then
    mkdir -p /var/log/kolla/chrony
fi
if [[ $(stat -c %a /var/log/kolla/chrony) != "755" ]]; then
    chmod 755 /var/log/kolla/chrony
fi
