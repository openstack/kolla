#!/bin/bash

set -o errexit

CMD="/usr/bin/cinder-api"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "cinder-manage db_sync" cinder
    exit 0
fi

exec $CMD $ARGS
