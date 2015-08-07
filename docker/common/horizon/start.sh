#!/bin/bash

set -o errexit

CMD="/usr/sbin/httpd"
ARGS="-DFOREGROUND"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
