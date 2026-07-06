#!/bin/bash

if [[ ! -d "/var/log/kolla/grafana" ]]; then
    mkdir -p /var/log/kolla/grafana
fi
if [[ $(stat -c %a /var/log/kolla/grafana) != "755" ]]; then
    chmod 755 /var/log/kolla/grafana
fi
