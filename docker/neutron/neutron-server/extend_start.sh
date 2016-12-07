#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head
    exit 0
fi

# Migrate database and exit if KOLLA_UPGRADE variable is set. This catches all cases
# of the KOLLA_UPGRADE variable being set, including empty.
if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    if [[ "${!NEUTRON_DB_EXPAND[@]}" ]]; then
        echo "Expanding database"
        neutron-db-manage upgrade --expand
    fi
    if [[ "${!NEUTRON_DB_CONTRACT[@]}" ]]; then
        echo "Contracting database"
        neutron-db-manage upgrade --contract
    fi
    exit 0
fi
