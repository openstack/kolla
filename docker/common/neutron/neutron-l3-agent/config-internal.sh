#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh

: ${USE_NAMESPACES:=true}

check_required_vars VERBOSE_LOGGING DEBUG_LOGGING

cfg=/etc/neutron/l3_agent.ini
neutron_conf=/etc/neutron/neutron.conf

# Logging
crudini --set $neutron_conf \
    DEFAULT \
    log_file \
    "${NEUTRON_L3_AGENT_LOG_FILE}"

# Configure l3_agent.ini
crudini --set $cfg \
    DEFAULT \
    verbose \
    "${VERBOSE_LOGGING}"
crudini --set $cfg \
    DEFAULT \
    debug \
    "${DEBUG_LOGGING}"
if [[ "${MECHANISM_DRIVERS}" =~ linuxbridge ]] ; then
    crudini --set $cfg \
        DEFAULT \
        interface_driver \
        "neutron.agent.linux.interface.BridgeInterfaceDriver"
    crudini --set $cfg \
        DEFAULT \
        gateway_external_network_id \
        ""
    crudini --set $cfg \
        DEFAULT \
        external_network_bridge \
        ""
elif [[ "${MECHANISM_DRIVERS}" =~ .*openvswitch* ]] ; then
    crudini --set $cfg \
        DEFAULT \
        interface_driver \
        "neutron.agent.linux.interface.OVSInterfaceDriver"
    crudini --set $cfg \
        DEFAULT \
        gateway_external_network_id \
        "${NEUTRON_FLAT_NETWORK_BRIDGE}"
    crudini --set $cfg \
        DEFAULT \
        external_network_bridge \
        "${NEUTRON_FLAT_NETWORK_BRIDGE}"
fi

crudini --set $cfg \
    DEFAULT \
    use_namespaces \
    "${USE_NAMESPACES}"

if [ "${USE_NAMESPACES}" == "false" ] ; then
    source /openrc
    # Create router if it does not exist
    /usr/bin/neutron router-list | grep admin-router || /usr/bin/neutron router-create admin-router
    # Set router-id
    crudini --set $cfg \
        DEFAULT \
        router_id \
        "$(/usr/bin/neutron router-list | awk '/ admin-router / {print $2}')"
elif [ "${USE_NAMESPACES}" == "true" ] ; then
    crudini --set $cfg \
        DEFAULT \
        router_delete_namespaces \
        "true"
fi

# TODO: SamYaple remove this section for thin neutron containers
# The reason we remove existing namespaces is because network namespaces don't
# persist between container restarts because the network proc mountpoint dies
# when the container mount namespace dies. The mountpoint in /run/netns does
# persist however, and that is all we are cleaning up here.

# Remove any existing qrouter namespaces
ip netns list | grep qrouter | while read -r line ; do
    ip netns delete $line
done

# Start L3 Agent
exec /usr/bin/neutron-l3-agent --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/l3_agent.ini --config-file /etc/neutron/fwaas_driver.ini --config-dir /etc/neutron
