#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    neutron-db-manage --subproject networking-sfc --config-file /etc/neutron/neutron.conf upgrade head
    exit 0
fi
