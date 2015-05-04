#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-nova.sh

cfg=/etc/nova/nova.conf

check_required_vars NOVA_NOVNC_PROXYCLIENT_IP

# Configures novnc to listen on all interfaces and instructs nova-compute to
# announce PROXYCLIENT_IP to the nova-vncproxy. Clients like Horizon will
# connect with this address.
# As such, PROXYCLIENT_IP is unique per compute node.
crudini --set $cfg DEFAULT vnc_enabled "True"
crudini --set $cfg DEFAULT vncserver_listen "0.0.0.0"
crudini --set $cfg DEFAULT vncserver_proxyclient_address "${NOVA_NOVNC_PROXYCLIENT_IP}"

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_COMPUTE_LOG_FILE}"

# set qmeu emulation if no hardware acceleration found
if [[ `egrep -c '(vmx|svm)' /proc/cpuinfo` == 0 ]]
then
    crudini --set $cfg libvirt virt_type qemu
fi

mkdir -p /var/lib/nova/instances
