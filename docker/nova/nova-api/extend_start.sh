#!/bin/bash

if [[ ! -d "/var/log/kolla/nova" ]]; then
    mkdir -p /var/log/kolla/nova
fi
if [[ $(stat -c %a /var/log/kolla/nova) != "755" ]]; then
    chmod 755 /var/log/kolla/nova
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    nova-manage db sync
    nova-manage api_db sync
    exit 0
fi
