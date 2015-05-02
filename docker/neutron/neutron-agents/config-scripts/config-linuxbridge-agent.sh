#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh
. /opt/kolla/config-sudoers.sh

: ${NEUTRON_FLAT_NETWORK_NAME:=physnet1}
: ${NEUTRON_FLAT_NETWORK_INTERFACE:=eth1}

check_required_vars PUBLIC_IP NEUTRON_FLAT_NETWORK_NAME \
                    NEUTRON_FLAT_NETWORK_INTERFACE

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
