#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    neutron-db-manage --subproject neutron upgrade head
    if [[ "${!NEUTRON_BOOTSTRAP_SERVICES[@]}" ]]; then
        for service in ${NEUTRON_BOOTSTRAP_SERVICES}; do
            neutron-db-manage --subproject $service upgrade head
        done
    fi
    exit 0
fi

# Migrate database and exit if KOLLA_UPGRADE variable is set. This catches all cases
# of the KOLLA_UPGRADE variable being set, including empty.
if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    if [[ "${!NEUTRON_DB_EXPAND[@]}" ]]; then
        DB_ACTION="--expand"
        echo "Expanding database"
    fi
    if [[ "${!NEUTRON_DB_CONTRACT[@]}" ]]; then
        DB_ACTION="--contract"
        echo "Contracting database"
    fi

    neutron-db-manage --subproject neutron upgrade $DB_ACTION
    if [[ "${!NEUTRON_ROLLING_UPGRADE_SERVICES[@]}" ]]; then
        for service in ${NEUTRON_ROLLING_UPGRADE_SERVICES}; do
            neutron-db-manage --subproject $service upgrade $DB_ACTION
        done
    fi
    exit 0
fi
