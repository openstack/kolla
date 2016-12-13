#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/kafka" ]]; then
    mkdir -p /var/log/kolla/kafka
fi
if [[ $(stat -c %a /var/log/kolla/kafka) != "755" ]]; then
    chmod 755 /var/log/kolla/kafka
fi
