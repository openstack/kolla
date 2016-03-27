#!/bin/bash

if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    mkdir -p /usr/lib/docker/plugins/kuryr
    exit 0
fi
