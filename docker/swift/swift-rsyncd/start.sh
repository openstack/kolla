#!/bin/bash

set -o errexit

CMD="/usr/bin/rsync"
ARGS="--daemon --no-detach --config=/etc/rsyncd.conf"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
