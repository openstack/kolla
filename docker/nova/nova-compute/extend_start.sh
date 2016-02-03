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
    sudo chown nova: /var/lib/nova/
    mkdir -p /var/lib/nova/instances
    # Only update permissions if permissions need to be updated
    if [[ $(stat -c %U:%G /var/lib/nova/instances) != "nova:nova" ]]; then
        sudo chown nova: /var/lib/nova/instances
    fi
    exit 0
fi
