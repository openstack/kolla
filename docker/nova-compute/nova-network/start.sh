#!/bin/sh

set -e

. /opt/kolla/config-nova.sh

/usr/sbin/brctl addbr br100
ip link set br100 up

# This is a dummy interface
ip link add flat0 type veth peer name flat1
ip link set flat0 up
ip link set flat1 up

exec /usr/bin/nova-network
