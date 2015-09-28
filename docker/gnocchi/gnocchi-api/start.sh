#!/bin/bash
set -o errexit

CMD="/usr/bin/gnocchi-api"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "gnocchi-manage db_sync" gnocchi
    exit 0
fi

exec $CMD $ARGS

