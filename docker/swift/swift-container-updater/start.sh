#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-container-updater"
ARGS="/etc/swift/container-updater.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
