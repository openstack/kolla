#!/bin/bash

set -o errexit

CMD="/usr/bin/swift-account-server"
ARGS="/etc/swift/account-server.conf --verbose"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

exec $CMD $ARGS
