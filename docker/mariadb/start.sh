#!/bin/bash

set -o errexit

# Loading common functions
source /opt/kolla/kolla-common.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

# Loading functions
source /opt/kolla/config/config-galera.sh

chown mysql: /var/lib/mysql

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]] && [[ ! -e /var/lib/mysql/cluster.exists ]]; then
    ARGS="--wsrep-new-cluster"
    touch /var/lib/mysql/cluster.exists
    populate_db
    bootstrap_db
    exec $CMD $ARGS
    exit 0
fi

echo "Running command: ${CMD}"
exec $CMD
