#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-object-server"
ARGS="/etc/swift/object-server.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
