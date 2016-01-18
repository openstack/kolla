#!/bin/bash

echo "run extended start"

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo chown mongodb: /var/lib/mongodb/
    exit 0
fi
