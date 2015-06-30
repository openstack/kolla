#!/bin/bash

set -o errexit

CMD="/usr/bin/keystone-all"
ARGS=""

# loading common functions
source /opt/kolla/kolla-common.sh

set_configs

# Bootstrap and exit if BOOTSTRAP variable is set
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -c "keystone-manage db_sync" keystone
    exit 0
fi

exec $CMD $ARGS
