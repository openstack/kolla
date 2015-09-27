#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

mkdir -p "/run/openvswitch"
if [[ ! -e "/etc/openvswitch/conf.db" ]]; then
    ovsdb-tool create "/etc/openvswitch/conf.db"
fi

exec $CMD
