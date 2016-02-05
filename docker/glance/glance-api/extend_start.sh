#!/bin/bash

if [[ ! -d "/var/log/kolla/glance" ]]; then
    mkdir -p /var/log/kolla/glance
fi
if [[ $(stat -c %a /var/log/kolla/glance) != "755" ]]; then
    chmod 755 /var/log/kolla/glance
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    glance-manage db_sync
    sudo chown -R glance: /var/lib/glance/
    exit 0
fi
