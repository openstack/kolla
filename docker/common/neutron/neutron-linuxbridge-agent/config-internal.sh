#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh

check_required_vars NEUTRON_FLAT_NETWORK_INTERFACE \
                    NEUTRON_FLAT_NETWORK_NAME \
                    PUBLIC_IP

cfg=/etc/neutron/plugins/ml2/ml2_conf.ini

# Configure ml2_conf.ini
if [[ ${TYPE_DRIVERS} =~ vxlan ]]; then
    crudini --set $cfg \
        vxlan \
        local_ip \
        "${PUBLIC_IP}"
fi

crudini --set $cfg \
    linux_bridge \
    physical_interface_mappings \
    "${NEUTRON_FLAT_NETWORK_NAME}:${NEUTRON_FLAT_NETWORK_INTERFACE}"

exec /usr/bin/neutron-linuxbridge-agent --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-dir /etc/neutron
