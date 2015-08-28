#!/bin/bash
set -o errexit

CMD="/usr/bin/murano-engine"
ARGS="--config-file /etc/murano/murano.conf"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
