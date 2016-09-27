#!/bin/bash

if [[ ! -d "/var/log/kolla/searchlight" ]]; then
    mkdir -p /var/log/kolla/searchlight
fi
if [[ $(stat -c %a /var/log/kolla/searchlight) != "755" ]]; then
    chmod 755 /var/log/kolla/searchlight
fi

. /usr/local/bin/kolla_searchlight_extend_start
