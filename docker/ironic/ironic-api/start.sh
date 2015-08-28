#!/bin/bash
set -o errexit

source /opt/kolla/kolla-common.sh

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "ironic-dbsync upgrade" ironic
    exit 0
fi

exec $CMD
