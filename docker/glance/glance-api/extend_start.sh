#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    glance-manage db_sync
    glance-manage db_load_metadefs
    sudo chown -R glance: /var/lib/glance/
    exit 0
fi
