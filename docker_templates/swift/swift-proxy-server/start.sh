#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-proxy-server"
ARGS="/etc/swift/proxy-server.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

source /opt/kolla/config-swift.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
