#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

modprobe ip_vs

# Workaround for bug #1485079
if [ -f /run/keepalived.pid ]; then
    rm /run/keepalived.pid
fi

exec $CMD
