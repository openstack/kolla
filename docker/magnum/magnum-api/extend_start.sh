#!/bin/bash

if [[ ! -d "/var/log/kolla/magnum" ]]; then
    mkdir -p /var/log/kolla/magnum
fi
if [[ $(stat -c %a /var/log/kolla/magnum) != "755" ]]; then
    chmod 755 /var/log/kolla/magnum
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    magnum-db-manage upgrade
    exit 0
fi
