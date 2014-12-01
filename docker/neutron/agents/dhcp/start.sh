#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh
. /sudoers.sh

: ${INTERFACE_DRIVER:=neutron.agent.linux.interface.BridgeInterfaceDriver}
: ${DHCP_DRIVER:=neutron.agent.linux.dhcp.Dnsmasq}
: ${USE_NAMESPACES:=false}

check_required_vars VERBOSE_LOGGING DEBUG_LOGGING

cfg=/etc/neutron/dhcp_agent.ini

# Configure dhcp_agent.ini
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
        dhcp_driver \
        "${DHCP_DRIVER}"
crudini --set $cfg \
        DEFAULT \
        use_namespaces \
        "${USE_NAMESPACES}"

# Start DHCP Agent
exec /usr/bin/neutron-dhcp-agent
