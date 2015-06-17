#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-nova.sh

cfg=/etc/nova/nova.conf

check_required_vars NOVA_VNCSERVER_PROXYCLIENT_ADDRESS NOVA_NOVNC_PROXY_PORT \
                    NOVA_NOVNC_BASE_ADDRESS

# Configures novnc to listen on all interfaces and instructs nova-compute to
# announce PROXYCLIENT_IP to the nova-vncproxy. Clients like Horizon will
# connect with this address.
# As such, NOVA_VNCSERVER_PROXYCLIENT_ADDRESS is unique per compute node.
crudini --set $cfg DEFAULT vnc_enabled "True"
crudini --set $cfg DEFAULT vncserver_listen "0.0.0.0"
crudini --set $cfg DEFAULT vncserver_proxyclient_address "${NOVA_VNCSERVER_PROXYCLIENT_ADDRESS}"
crudini --set $cfg DEFAULT novncproxy_base_url "http://${NOVA_NOVNC_BASE_ADDRESS}:${NOVA_NOVNC_PROXY_PORT}/vnc_auto.html"

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_COMPUTE_LOG_FILE}"

# set qmeu emulation if no hardware acceleration found
if [[ `egrep -c '(vmx|svm)' /proc/cpuinfo` == 0 ]]; then
    crudini --set $cfg libvirt virt_type qemu
fi

mkdir -p /var/lib/nova/instances
