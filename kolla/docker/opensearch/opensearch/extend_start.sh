#!/bin/bash

if [[ ! -d "/var/log/kolla/opensearch" ]]; then
    mkdir -p /var/log/kolla/opensearch
fi
if [[ $(stat -c %a /var/log/kolla/opensearch) != "755" ]]; then
    chmod 755 /var/log/kolla/opensearch
fi
