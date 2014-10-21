#!/bin/sh

set -e

. /opt/kolla/config-common.sh
. /opt/kolla/config-nova.sh

/usr/sbin/brctl addbr br100

exec /usr/bin/nova-network
