#!/bin/bash

if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo chown zookeeper: /var/lib/zookeeper
    exit 0
fi
