#!/bin/bash

set -e

. /opt/kolla/config-nova-compute.sh

sleep 6

echo "Starting nova-compute."
exec /usr/bin/nova-compute --config-file /etc/nova/nova.conf
