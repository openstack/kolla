#!/bin/bash
set -o errexit

CMD="/usr/bin/designate-pool-manager"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

exec $CMD $ARGS
