#!/bin/sh

set -e

. /opt/kolla/config-nova.sh

check_required_vars NOVA_DB_NAME NOVA_SCHEDULER_LOG_FILE
fail_unless_db $NOVA_DB_NAME

cfg=/etc/nova/nova.conf

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_SCHEDULER_LOG_FILE}"

exec /usr/bin/nova-scheduler
