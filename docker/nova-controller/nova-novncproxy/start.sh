#!/bin/bash
set -e
. /opt/kolla/kolla-common.sh

cfg=/etc/nova/nova.conf

check_required_vars PUBLIC_IP NOVA_NOVNC_PROXY_SERVICE_HOST NOVA_NOVNC_PROXY_PORT \
                    NOVA_NOVNC_BASE_ADDRESS

crudini --set $cfg DEFAULT log_file "${NOVA_NOVNCPROXY_LOG_FILE}"

# Listen on all interfaces on port $NOVA_NOVNC_PROXY_PORT for incoming novnc
# requests.
# The base_url is given to clients to connect to, like Horizon, so this could
# very well be fancy DNS name.
echo Configuring VNC...
crudini --set $cfg DEFAULT vnc_enabled "True"
crudini --set $cfg DEFAULT novncproxy_host "${NOVA_NOVNC_PROXY_SERVICE_HOST}"
crudini --set $cfg DEFAULT novncproxy_port "${NOVA_NOVNC_PROXY_PORT}"
crudini --set $cfg DEFAULT novncproxy_base_url "http://${NOVA_NOVNC_BASE_ADDRESS}:${NOVA_NOVNC_PROXY_PORT}/vnc_auto.html"

echo Starting nova-novncproxy
exec /usr/bin/nova-novncproxy
