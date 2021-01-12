#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/storm" ]]; then
    mkdir -p /var/log/kolla/storm
fi
if [[ $(stat -c %a /var/log/kolla/storm) != "755" ]]; then
    chmod 755 /var/log/kolla/storm
fi
