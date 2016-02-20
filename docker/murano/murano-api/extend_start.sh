#!/bin/bash

if [[ ! -d "/var/log/kolla/murano" ]]; then
    mkdir -p /var/log/kolla/murano
fi
if [[ $(stat -c %a /var/log/kolla/murano) != "755" ]]; then
    chmod 755 /var/log/kolla/murano
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    murano-db-manage --config-file /etc/murano/murano.conf upgrade
    exit 0
fi
