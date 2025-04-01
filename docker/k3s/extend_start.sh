#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/k3s" ]]; then
    mkdir -p /var/log/kolla/k3s
fi
if [[ $(stat -c %a /var/log/kolla/k3s) != "755" ]]; then
    chmod 755 /var/log/kolla/k3s
fi

if [[ $(stat -c %U /var/lib/k3s/) != "k3s" ]]; then
    sudo chown k3s: /var/lib/k3s/
fi
