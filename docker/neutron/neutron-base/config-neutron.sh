#!/bin/sh

set -e

. /opt/kolla/kolla-common.sh

# Database
: ${NEUTRON_DB_NAME:=neutron}
: ${NEUTRON_DB_USER:=neutron}
: ${NEUTRON_DB_PASSWORD:=password}
# Keystone
: ${ADMIN_TENANT_NAME:=admin}
: ${NEUTRON_KEYSTONE_USER:=neutron}
: ${NEUTRON_KEYSTONE_PASSWORD:=password}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${KEYSTONE_ADMIN_SERVICE_HOST:=127.0.0.1}
: ${KEYSTONE_PUBLIC_SERVICE_HOST:=127.0.0.1}
: ${KEYSTONE_ADMIN_SERVICE_PORT:=35357}
: ${KEYSTONE_PUBLIC_SERVICE_PORT:=5000}
: ${KEYSTONE_REGION:=RegionOne}
# RabbitMQ
: ${RABBIT_HOST:=$RABBITMQ_SERVICE_HOST}
: ${RABBIT_USER:=guest}
: ${RABBIT_PASSWORD:=guest}
# Logging
: ${VERBOSE_LOGGING:=true}
: ${DEBUG_LOGGING:=false}
# Networking
: ${NEUTRON_FLAT_NETWORK_NAME:=physnet1}
# Paste configuration file
: ${API_PASTE_CONFIG:=/usr/share/neutron/api-paste.ini}

check_required_vars NEUTRON_KEYSTONE_PASSWORD NEUTRON_API_PASTE_CONFIG \
                    KEYSTONE_PUBLIC_SERVICE_HOST RABBITMQ_SERVICE_HOST

core_cfg=/etc/neutron/neutron.conf
ml2_cfg=/etc/neutron/plugins/ml2/ml2_conf.ini

# Logging
crudini --set $core_cfg \
        DEFAULT \
        log_dir \
        "${NEUTRON_LOG_DIR}"
crudini --set $core_cfg \
        DEFAULT \
        verbose \
        "${VERBOSE_LOGGING}"
crudini --set $core_cfg \
        DEFAULT \
        debug \
        "${DEBUG_LOGGING}"

# Paste config
crudini --set $core_cfg \
        DEFAULT \
        api_paste_config \
        "${NEUTRON_API_PASTE_CONFIG}"

# Rabbit
crudini --set $core_cfg \
        DEFAULT \
        rabbit_host \
        "${RABBIT_HOST}"
crudini --set $core_cfg \
        DEFAULT \
        rabbit_userid \
        "${RABBIT_USER}"
crudini --set $core_cfg \
        DEFAULT \
        rabbit_password \
        "${RABBIT_PASSWORD}"

# Locking
crudini --set $core_cfg \
        DEFAULT \
        lock_path \
        "/var/lock/neutron"

# Keystone
crudini --set $core_cfg \
        DEFAULT \
        auth_strategy \
        "keystone"
crudini --set $core_cfg \
        keystone_authtoken \
        auth_uri \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
crudini --set $core_cfg \
        keystone_authtoken \
        identity_uri \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}"
crudini --set $core_cfg \
        keystone_authtoken \
        admin_tenant_name \
        "${ADMIN_TENANT_NAME}"
crudini --set $core_cfg \
        keystone_authtoken \
        admin_user \
        "${NEUTRON_KEYSTONE_USER}"
crudini --set $core_cfg \
        keystone_authtoken \
        admin_password \
        "${NEUTRON_KEYSTONE_PASSWORD}"

# Rootwrap
crudini --set $core_cfg \
        agent \
        root_helper \
        "sudo neutron-rootwrap /etc/neutron/rootwrap.conf"

# neutron.conf ml2 configuration
crudini --set $core_cfg \
        DEFAULT \
        core_plugin \
        "neutron.plugins.ml2.plugin.Ml2Plugin"
crudini --set $core_cfg \
        DEFAULT \
        service_plugins \
        "neutron.services.l3_router.l3_router_plugin.L3RouterPlugin,neutron.services.loadbalancer.plugin.LoadBalancerPlugin,neutron.services.vpn.plugin.VPNDriverPlugin,neutron.services.metering.metering_plugin.MeteringPlugin"
crudini --set $core_cfg \
        DEFAULT \
        allow_overlapping_ips \
        "True"

# Configure ml2_conf.ini
crudini --set $ml2_cfg \
        ml2 \
        type_drivers \
        "${TYPE_DRIVERS}"
crudini --set $ml2_cfg \
        ml2 \
        tenant_network_types \
        "${TENANT_NETWORK_TYPES}"
crudini --set $ml2_cfg \
        ml2 \
        mechanism_drivers \
        "${MECHANISM_DRIVERS}"

if [[ ${TYPE_DRIVERS} =~ .*flat.* ]]; then
  crudini --set $ml2_cfg \
          ml2_type_flat \
          flat_networks \
          ${NEUTRON_FLAT_NETWORK_NAME}
fi

if [[ ${TYPE_DRIVERS} =~ .*vxlan.* ]]; then
  crudini --set $ml2_cfg \
          ml2_type_vxlan \
          vxlan_group \
          ""
  crudini --set $ml2_cfg \
          ml2_type_vxlan \
          vni_ranges \
          "1:1000"
  crudini --set $ml2_cfg \
          vxlan \
          enable_vxlan \
          "True"
  crudini --set $ml2_cfg \
          vxlan \
          vxlan_group \
          ""
  crudini --set $ml2_cfg \
          vxlan \
          l2_population \
          "True"
  crudini --set $ml2_cfg \
          agent \
          tunnel_types \
          "vxlan"
  crudini --set $ml2_cfg \
          agent \
          vxlan_udp_port \
          "4789"
  crudini --set $core_cfg \
          DEFAULT \
          network_device_mtu \
          "1450"
fi

crudini --set $ml2_cfg \
        l2pop \
        agent_boot_time \
        "180"
crudini --set $ml2_cfg \
        securitygroup \
        enable_security_group \
        "True"
crudini --set $ml2_cfg \
        securitygroup \
        enable_ipset \
        "True"

if [[ ${MECHANISM_DRIVERS} =~ .*linuxbridge.* ]]; then
  firewall_driver="neutron.agent.linux.iptables_firewall.IptablesFirewallDriver"
elif [[ ${MECHANISM_DRIVERS} == "openvswitch" ]]; then
  firewall_driver="neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver"
fi

  crudini --set $ml2_cfg \
          securitygroup \
          firewall_driver \
          "$firewall_driver"

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
export OS_USERNAME="${NEUTRON_KEYSTONE_USER}"
export OS_PASSWORD="${NEUTRON_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF
