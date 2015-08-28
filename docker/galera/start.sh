#!/bin/bash

set -o errexit

CMD="/usr/bin/mysqld_safe"
ARGS=""

# loading common functions
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

# loading functions
source /opt/kolla/config/config-galera.sh

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]] && [[ ! -e /var/lib/mysql/cluster.exists ]]; then
    ARGS="--wsrep-new-cluster"
    touch /var/lib/mysql/cluster.exists
    populate_db
    bootstrap_db
fi

exec $CMD $ARGS
