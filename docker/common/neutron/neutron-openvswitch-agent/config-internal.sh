#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh

: ${NEUTRON_FLAT_NETWORK_NAME:=physnet1}
: ${NEUTRON_FLAT_NETWORK_INTERFACE:=eth1}

check_required_vars PUBLIC_IP NEUTRON_FLAT_NETWORK_NAME \
                    NEUTRON_FLAT_NETWORK_INTERFACE

if ! ovs-vsctl show |grep ${NEUTRON_FLAT_NETWORK_INTERFACE} > /dev/null; then
    ovs-vsctl add-br ${NEUTRON_FLAT_NETWORK_INTERFACE}
fi

cfg=/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini

# Configure ml2_conf.ini
if [[ ${TYPE_DRIVERS} =~ vxlan ]]; then
    crudini --set $cfg \
        vxlan \
        local_ip \
        "${PUBLIC_IP}"
fi

crudini --set $cfg \
    ovs \
    bridge_mappings \
    "${NEUTRON_FLAT_NETWORK_NAME}:${NEUTRON_FLAT_NETWORK_INTERFACE}"

crudini --set $cfg \
    ovs \
    tenant_network_type \
    "${TENANT_NETWORK_TYPES}"

if [[ ${TENANT_NETWORK_TYPES} =~ "vlan" ]];then
    crudini --set $cfg \
        ovs \
        network_vlan_ranges \
        "${NEUTRON_VLAN_NETWORK_NAME}:${NEUTRON_NETWORK_VLAN_RANGES}"
fi

exec /usr/bin/neutron-openvswitch-agent --config-file /etc/neutron/neutron.conf --config-file $cfg
