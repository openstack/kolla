#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/sensu" ]]; then
    mkdir -p /var/log/kolla/sensu
fi
if [[ $(stat -c %a /var/log/kolla/sensu) != "755" ]]; then
    chmod 755 /var/log/kolla/sensu
fi
