#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh
. /sudoers.sh

: ${BRIDGE_PHYSICAL_INTERFACE:=eth1}
: ${ML2_FLAT_NETWORK:=physnet1}

cfg=/etc/neutron/plugins/ml2/ml2_conf.ini

# Configure ml2_conf.ini
crudini --set $cfg \
        ml2_type_flat \
        flat_networks \
        "${ML2_FLAT_NETWORK}"
crudini --set $cfg \
        vxlan \
        local_ip \
        "${PUBLIC_IP}"
crudini --set $cfg \
        linux_bridge \
        physical_interface_mappings \
        "${ML2_FLAT_NETWORK}:${BRIDGE_PHYSICAL_INTERFACE}"

#Initialization scripts expect a symbolic link
/usr/bin/ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

# Start the linux bridge agent.
exec /usr/bin/neutron-linuxbridge-agent
