#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    octavia-db-manage upgrade head
    octavia-db-manage upgrade_persistence
    exit 0
fi

. /usr/local/bin/kolla_httpd_setup
