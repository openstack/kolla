#!/bin/bash

# TODO(dszumski): When Nova Conductor in Kolla Ansible supports triggering DB
# operations, we should review this script and remove any duplicate
# operations. This is probably anything that isn't to do with the API.

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    nova-manage api_db sync
    nova-manage db sync
    nova-manage db online_data_migrations
    exit 0
fi

if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    nova-manage api_db sync
    nova-manage db sync
    exit 0
fi

if [[ "${!KOLLA_OSM[@]}" ]]; then
    nova-manage db online_data_migrations
    exit 0
fi

if [[ "${!KOLLA_UPGRADE_CHECK[@]}" ]]; then
    nova-status upgrade check
    exit $?
fi

. /usr/local/bin/kolla_httpd_setup
