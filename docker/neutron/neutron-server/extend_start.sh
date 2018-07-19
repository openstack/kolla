#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    OPTS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini"
    neutron-db-manage ${OPTS} upgrade head
    neutron-db-manage ${OPTS} --subproject neutron-fwaas upgrade head
    neutron-db-manage ${OPTS} --subproject neutron-vpnaas upgrade head
    exit 0
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP and NEUTRON_SFC_ENABLED variables are set.
# This catches all cases of the KOLLA_BOOTSTRAP and NEUTRON_SFC_ENABLED variable
# being set, including empty.
if [[ "${!NEUTRON_SFC_BOOTSTRAP[@]}" ]]; then
    neutron-db-manage --subproject networking-sfc --config-file /etc/neutron/neutron.conf upgrade head
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

    if [[ "${!NEUTRON_ROLLING_UPGRADE_SERVICES[@]}" ]]; then
        for service in ${NEUTRON_ROLLING_UPGRADE_SERVICES}; do
            neutron-db-manage --subproject $service upgrade $DB_ACTION
        done
    fi
    exit 0
fi
