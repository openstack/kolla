#!/bin/sh

set -e

. /opt/kolla/config-nova.sh

check_required_vars NOVA_DB_NAME
check_for_db $NOVA_DB_NAME

exec /usr/bin/nova-scheduler
