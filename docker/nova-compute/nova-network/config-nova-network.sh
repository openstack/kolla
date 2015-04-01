#!/bin/sh

. /opt/kolla/config-nova.sh

check_required_vars NOVA_NETWORK_LOG_FILE

cfg=/etc/nova/nova.conf

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_NETWORK_LOG_FILE}"

# Configure eth1 as a physcial interface for nova flat network
cat > /etc/sysconfig/network-scripts/ifcfg-$FLAT_INTERFACE <<EOF
DEVICE="$FLAT_INTERFACE"
BOOTPROTO="none"
ONBOOT="yes"
TYPE="Ethernet"
EOF

/usr/sbin/ifup $FLAT_INTERFACE

cfg=/etc/nova/nova.conf

crudini --set $cfg DEFAULT network_manager nova.network.manager.FlatDHCPManager
crudini --set $cfg DEFAULT firewall_driver nova.virt.libvirt.firewall.IptablesFirewallDriver
crudini --set $cfg DEFAULT network_size 254
crudini --set $cfg DEFAULT allow_same_net_traffic False
crudini --set $cfg DEFAULT multi_host True
crudini --set $cfg DEFAULT send_arp_for_ha True
crudini --set $cfg DEFAULT share_dhcp_address True
crudini --set $cfg DEFAULT force_dhcp_release True
crudini --set $cfg DEFAULT flat_network_bridge br100
