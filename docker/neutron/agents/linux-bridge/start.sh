#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh
. /sudoers.sh

: ${NEUTRON_FLAT_NETWORK_NAME:=physnet1}
: ${NEUTRON_FLAT_NETWORK_INTERFACE:=eth1}

check_required_vars PUBLIC_IP

cfg=/etc/neutron/plugins/ml2/ml2_conf.ini

# Configure ml2_conf.ini
crudini --set $cfg \
        vxlan \
        local_ip \
        "${PUBLIC_IP}"
crudini --set $cfg \
        linux_bridge \
        physical_interface_mappings \
        "${NEUTRON_FLAT_NETWORK_NAME}:${NEUTRON_FLAT_NETWORK_INTERFACE}"

#Initialization scripts expect a symbolic link
/usr/bin/ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

# Start the linux bridge agent.
exec /usr/bin/neutron-linuxbridge-agent
