#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    glance-manage db_sync
    glance-manage db_load_metadefs
    exit 0
fi

# Migrate database and exit if KOLLA_UPGRADE variable is set. This catches all cases
# of the KOLLA_UPGRADE variable being set, including empty.
if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    if [[ "${!GLANCE_DB_EXPAND[@]}" ]]; then
        echo "Expanding database"
        glance-manage db expand
    fi
    if [[ "${!GLANCE_DB_MIGRATE[@]}" ]]; then
        echo "Migrating database"
        glance-manage db migrate
    fi
    if [[ "${!GLANCE_DB_CONTRACT[@]}" ]]; then
        echo "Contracting database"
        glance-manage db contract
    fi
    exit 0
fi
