#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-account-auditor"
ARGS="/etc/swift/account-auditor.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
