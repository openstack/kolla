#!/bin/bash
set -e

. /opt/kolla/config-nova.sh

cfg=/etc/nova/nova.conf

crudini --set $cfg DEFAULT log_file "${NOVA_CONSOLEAUTH_LOG_FILE}"

echo Starting nova-consoleauth
exec /usr/bin/nova-consoleauth
