#!/bin/bash
set -e
. /opt/kolla/kolla-common.sh

cfg=/etc/nova/nova.conf

check_required_vars PUBLIC_IP NOVA_NOVNC_PROXY_SERVICE_HOST NOVA_NOVNC_PROXY_PORT \
                    NOVA_NOVNC_BASE_ADDRESS NOVA_VNCSERVER_LISTEN_ADDRESS \
                    NOVA_VNCSERVER_PROXYCLIENT_ADDRESS

crudini --set $cfg DEFAULT log_file "${NOVA_NOVNCPROXY_LOG_FILE}"

# Listen on all interfaces on port $NOVA_NOVNC_PROXY_PORT for incoming novnc
# requests.
# The base_url is given to clients to connect to, like Horizon, so this could
# very well be fancy DNS name.
echo Configuring VNC...
crudini --set $cfg DEFAULT vncserver_listen "${NOVA_VNCSERVER_LISTEN_ADDRESS}"
crudini --set $cfg DEFAULT vncserver_proxyclient_address "${NOVA_VNCSERVER_PROXYCLIENT_ADDRESS}"

echo Starting nova-novncproxy
exec /usr/bin/nova-novncproxy
