#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    glance-manage db_sync
    sudo chown -R glance: /var/lib/glance/
    echo "check chown"
    ls /var/lib/glance/
    echo "change galnce folder to glance user"
    exit 0
fi
