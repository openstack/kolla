#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh

: ${DHCP_DRIVER:=neutron.agent.linux.dhcp.Dnsmasq}
: ${USE_NAMESPACES:=true}
: ${DELETE_NAMESPACES:=true}
: ${DNSMASQ_CONFIG_FILE:=/etc/neutron/dnsmasq/dnsmasq-neutron.conf}
: ${ROOT_HELPER:=sudo neutron-rootwrap /etc/neutron/rootwrap.conf}

mkdir -p $(dirname $DNSMASQ_CONFIG_FILE)

check_required_vars VERBOSE_LOGGING DEBUG_LOGGING MECHANISM_DRIVERS \
                    DHCP_DRIVER USE_NAMESPACES DELETE_NAMESPACES \
                    NEUTRON_LOG_DIR DNSMASQ_CONFIG_FILE \

cfg=/etc/neutron/dhcp_agent.ini
neutron_conf=/etc/neutron/neutron.conf

# Workaround bug in dhclient in cirros images which does not correctly
# handle setting checksums of packets when using hardware with checksum
# offloading.  See:
# https://www.rdoproject.org/forum/discussion/567/packstack-allinone-grizzly-cirros-image-cannot-get-a-dhcp-address-when-a-centos-image-can/p1

/usr/sbin/iptables -A POSTROUTING -t mangle -p udp --dport bootpc \
    -j CHECKSUM --checksum-fill

if [[ ${MECHANISM_DRIVERS} =~ linuxbridge ]]; then
    interface_driver="neutron.agent.linux.interface.BridgeInterfaceDriver"
elif [[ ${MECHANISM_DRIVERS} == "openvswitch" ]]; then
    interface_driver="neutron.agent.linux.interface.OVSInterfaceDriver"
fi

# Logging
crudini --set $neutron_conf \
    DEFAULT \
    log_file \
    "${NEUTRON_DHCP_AGENT_LOG_FILE}"

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
    "$interface_driver"
crudini --set $cfg \
    DEFAULT \
    dhcp_driver \
    "${DHCP_DRIVER}"
crudini --set $cfg \
    DEFAULT \
    use_namespaces \
    "${USE_NAMESPACES}"
crudini --set $cfg \
    DEFAULT \
    delete_namespaces \
    "${DELETE_NAMESPACES}"
crudini --set $cfg \
    DEFAULT \
    dnsmasq_config_file \
    "${DNSMASQ_CONFIG_FILE}"
crudini --set $cfg \
    DEFAULT \
    root_helper \
    "${ROOT_HELPER}"

cat > ${DNSMASQ_CONFIG_FILE} <<EOF
dhcp-option-force=26,1450
log-facility=${NEUTRON_LOG_DIR}/neutron-dnsmasq.log
EOF

# TODO: SamYaple remove this section for thin neutron containers
# The reason we remove existing namespaces is because network namespaces don't
# persist between container restarts because the network proc mountpoint dies
# when the container mount namespace dies. The mountpoint in /run/netns does
# persist however, and that is all we are cleaning up here.

# Remove any existing qdhcp namespaces
ip netns list | grep qdhcp | while read -r line ; do
    ip netns delete $line
done

# Start DHCP Agent
exec /usr/bin/neutron-dhcp-agent --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/dhcp_agent.ini --config-dir /etc/neutron
