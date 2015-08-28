#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-container-server"
ARGS="/etc/swift/container-server.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

source /opt/kolla/config-swift.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
