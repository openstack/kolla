#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

mkdir -p "/run/openvswitch"
if [[ ! -e "/etc/openvswitch/conf.db" ]]; then
    ovsdb-tool create "/etc/openvswitch/conf.db"
fi

exec $CMD
