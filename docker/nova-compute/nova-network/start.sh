#!/bin/sh

set -e

. /opt/kolla/config-common.sh
. /opt/kolla/config-nova.sh

exec /usr/bin/nova-network
