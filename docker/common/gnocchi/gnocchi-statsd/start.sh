#!/bin/bash
set -o errexit

CMD="/usr/bin/gnocchi-statsd"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS

