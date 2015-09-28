#!/bin/bash
set -o errexit

CMD="/usr/bin/ceilometer-agent-compute"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

exec $CMD $ARGS
