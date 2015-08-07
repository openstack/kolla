#!/bin/bash
set -o errexit

CMD="/usr/sbin/keepalived"
ARGS="-nld -p /run/keepalived.pid"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
