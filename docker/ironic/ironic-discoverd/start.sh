#!/bin/bash
set -o errexit

CMD="/usr/bin/ironic-discoverd"
ARGS=""

source /opt/kolla/kolla-common.sh
set_configs

exec $CMD $ARGS
