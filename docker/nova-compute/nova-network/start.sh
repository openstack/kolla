#!/bin/sh

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-nova.sh

/usr/sbin/brctl addbr br100

exec /usr/bin/nova-network
