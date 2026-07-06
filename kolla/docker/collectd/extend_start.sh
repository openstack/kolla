#!/bin/bash

if [[ ! -d "/var/log/kolla/collectd" ]]; then
    mkdir -p /var/log/kolla/collectd
fi
if [[ $(stat -c %a /var/log/kolla/collectd) != "755" ]]; then
    chmod 755 /var/log/kolla/collectd
fi
