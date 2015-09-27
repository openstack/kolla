#!/bin/bash
set -o errexit

CMD="/usr/sbin/named"
ARGS="-u named -g"

# Execute config strategy
source /opt/kolla/kolla-common.sh

exec $CMD $ARGS
