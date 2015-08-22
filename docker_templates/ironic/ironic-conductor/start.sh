#!/bin/bash
set -o errexit

CMD="/usr/bin/ironic-conductor"
ARGS=""

source /opt/kolla/kolla-common.sh
set_configs

exec $CMD $ARGS
