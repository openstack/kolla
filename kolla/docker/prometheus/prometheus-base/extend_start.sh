#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/prometheus" ]]; then
    mkdir -p /var/log/kolla/prometheus
fi
if [[ $(stat -c %a /var/log/kolla/prometheus) != "755" ]]; then
    chmod 755 /var/log/kolla/prometheus
fi
