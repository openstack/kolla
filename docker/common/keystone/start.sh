#!/bin/bash

set -o errexit

CMD="/usr/sbin/httpd"
ARGS="-DFOREGROUND"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "keystone-manage db_sync" keystone
    exit 0
fi

exec $CMD $ARGS
