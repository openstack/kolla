#!/bin/bash

echo "run extended start"

if [[ ! -d "/var/log/kolla/mongodb" ]]; then
    mkdir -p /var/log/kolla/mongodb
fi

if [[ $(stat -c %a /var/log/kolla/mongodb) != "755" ]]; then
    chmod 755 /var/log/kolla/mongodb
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo chown mongodb: /var/lib/mongodb/
    exit 0
fi
