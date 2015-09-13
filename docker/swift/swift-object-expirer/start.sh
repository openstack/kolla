#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-object-expirer"
ARGS="/etc/swift/object-expirer.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
