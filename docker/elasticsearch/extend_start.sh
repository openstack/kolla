#!/bin/bash

if [[ ! -d "/var/log/kolla/elasticsearch" ]]; then
    mkdir -p /var/log/kolla/elasticsearch
fi
if [[ $(stat -c %a /var/log/kolla/elasticsearch) != "755" ]]; then
    chmod 755 /var/log/kolla/elasticsearch
fi

# Only update permissions if permissions need to be updated
if [[ $(stat -c %U:%G /var/lib/elasticsearch/data) != "elasticsearch:elasticsearch" ]]; then
    sudo chown elasticsearch: /var/lib/elasticsearch/data
fi
