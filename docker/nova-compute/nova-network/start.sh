#!/bin/sh

set -e

. /opt/kolla/config-nova-network.sh

# Start nova-network
exec /usr/bin/nova-network
