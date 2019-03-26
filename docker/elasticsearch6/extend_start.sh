#!/bin/bash

if [[ ! -d "/var/log/kolla/elasticsearch" ]]; then
    mkdir -p /var/log/kolla/elasticsearch
fi
if [[ $(stat -c %a /var/log/kolla/elasticsearch) != "755" ]]; then
    chmod 755 /var/log/kolla/elasticsearch
fi
