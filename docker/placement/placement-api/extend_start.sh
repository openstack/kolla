#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    placement-manage db sync
    placement-manage db online_data_migrations
    exit 0
fi

# DB synchronisation. To be executed prior to upgrading services.
if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    placement-manage db sync
    exit 0
fi

# Online data migrations. To be executed after upgrading services.
if [[ "${!KOLLA_OSM[@]}" ]]; then
    placement-manage db online_data_migrations
    exit 0
fi

. /usr/local/bin/kolla_httpd_setup
