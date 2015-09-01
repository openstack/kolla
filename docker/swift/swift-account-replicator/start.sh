#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-account-replicator"
ARGS="/etc/swift/account-replicator.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
