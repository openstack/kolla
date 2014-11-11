#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh
. /sudoers.sh

: ${INTERFACE_DRIVER:=neutron.agent.linux.interface.BridgeInterfaceDriver}
: ${USE_NAMESPACES:=false}

cfg=/etc/neutron/l3_agent.ini

# Configure l3_agent.ini
crudini --set $cfg \
        DEFAULT \
        verbose \
        "${VERBOSE_LOGGING}"
crudini --set $cfg \
        DEFAULT \
        debug \
        "${DEBUG_LOGGING}"
crudini --set $cfg \
        DEFAULT \
        interface_driver \
        "${INTERFACE_DRIVER}"
crudini --set $cfg \
        DEFAULT \
        gateway_external_network_id \
        ""
crudini --set $cfg \
        DEFAULT \
        external_network_bridge \
        ""
crudini --set $cfg \
        DEFAULT \
        use_namespaces \
        "${USE_NAMESPACES}"

if [ "${USE_NAMESPACES}" == "false" ] || [ "${USE_NAMESPACES}" == "False" ] ; then
  # source Keystone credential file
  source /openrc
  # Create router if it does not exist
  /usr/bin/neutron router-list | grep admin-router || /usr/bin/neutron router-create admin-router
  # Set router-id
  crudini --set $cfg \
        DEFAULT \
        router_id \
        "$(/usr/bin/neutron router-list | awk '/ admin-router / {print $2}')"
fi

# Start L3 Agent
exec /usr/bin/neutron-l3-agent --config-file /usr/share/neutron/neutron-dist.conf --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/l3_agent.ini --config-file /etc/neutron/fwaas_driver.ini
