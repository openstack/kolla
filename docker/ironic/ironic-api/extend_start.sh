#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    ironic-dbsync upgrade
    ironic-dbsync online_data_migrations
    exit 0
fi

if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    ironic-dbsync upgrade
    exit 0
fi

if [[ "${!KOLLA_OSM[@]}" ]]; then
    ironic-dbsync online_data_migrations
    exit 0
fi

. /usr/local/bin/kolla_httpd_setup
