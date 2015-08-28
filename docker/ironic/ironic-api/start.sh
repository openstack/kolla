#!/bin/bash
set -o errexit

CMD="/usr/bin/ironic-api"
ARGS=""

source /opt/kolla/kolla-common.sh
set_configs

exec $CMD $ARGS
