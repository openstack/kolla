#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/zookeeper" ]]; then
    mkdir -p /var/log/kolla/zookeeper
fi
if [[ $(stat -c %a /var/log/kolla/zookeeper) != "755" ]]; then
    chmod 755 /var/log/kolla/zookeeper
fi
