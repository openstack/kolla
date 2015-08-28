#!/bin/bash
set -o errexit

CMD="/usr/sbin/keepalived"
ARGS="-nld -p /run/keepalived.pid"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

modprobe ip_vs

# Workaround for bug #1485079
if [ -f /run/keepalived.pid ]; then
    rm /run/keepalived.pid
fi

exec $CMD $ARGS
