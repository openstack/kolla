#!/bin/sh

. /opt/kolla/kolla-common.sh

: ${NOVA_DB_USER:=nova}
: ${NOVA_DB_NAME:=nova}
: ${NOVA_KEYSTONE_USER:=admin}
: ${NOVA_KEYSTONE_PASSWORD:=kolla}
: ${ADMIN_TENANT_NAME:=admin}
: ${RABBIT_USERID:=guest}
: ${RABBIT_PASSWORD:=guest}
: ${NETWORK_MANAGER:=nova}
: ${FLAT_NETWORK:=eth1}
: ${PUBLIC_NETWORK:=eth0}

check_required_vars KEYSTONE_ADMIN_TOKEN NOVA_DB_PASSWORD \
                    RABBITMQ_SERVICE_HOST GLANCE_API_SERVICE_HOST \
                    KEYSTONE_PUBLIC_SERVICE_HOST PUBLIC_IP \
                    PUBLIC_INTERFACE FLAT_INTERFACE

cfg=/etc/nova/nova.conf

crudini --set $cfg DEFAULT amqp_durable_queues False
crudini --set $cfg DEFAULT rabbit_host ${RABBITMQ_SERVICE_HOST}
crudini --set $cfg DEFAULT rabbit_port 5672
crudini --set $cfg DEFAULT rabbit_hosts ${RABBITMQ_SERVICE_HOST}:5672
crudini --set $cfg DEFAULT rabbit_use_ssl False
crudini --set $cfg DEFAULT rabbit_userid ${RABBIT_USERID}
crudini --set $cfg DEFAULT rabbit_password "${RABBIT_PASSWORD}"
crudini --set $cfg DEFAULT rabbit_virtual_host /
crudini --set $cfg DEFAULT rabbit_ha_queues False
crudini --set $cfg DEFAULT rpc_backend nova.openstack.common.rpc.impl_kombu
crudini --set $cfg DEFAULT enabled_apis ec2,osapi_compute,metadata
crudini --set $cfg DEFAULT ec2_listen 0.0.0.0
crudini --set $cfg DEFAULT osapi_compute_listen 0.0.0.0
crudini --set $cfg DEFAULT osapi_compute_workers 8
crudini --set $cfg DEFAULT metadata_listen 0.0.0.0
crudini --set $cfg DEFAULT metadata_workers 8
crudini --set $cfg DEFAULT service_down_time 60
crudini --set $cfg DEFAULT rootwrap_config /etc/nova/rootwrap.conf
crudini --set $cfg DEFAULT auth_strategy keystone
crudini --set $cfg DEFAULT use_forwarded_for False
crudini --set $cfg DEFAULT novncproxy_host 0.0.0.0
crudini --set $cfg DEFAULT novncproxy_port 6080
crudini --set $cfg DEFAULT glance_api_servers ${GLANCE_API_SERVICE_HOST}:9292
crudini --set $cfg DEFAULT metadata_host ${PUBLIC_IP}
crudini --set $cfg DEFAULT cpu_allocation_ratio 16.0
crudini --set $cfg DEFAULT ram_allocation_ratio 1.5
crudini --set $cfg DEFAULT scheduler_default_filters RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,CoreFilter
crudini --set $cfg DEFAULT compute_driver nova.virt.libvirt.LibvirtDriver
crudini --set $cfg DEFAULT vif_plugging_is_fatal True
crudini --set $cfg DEFAULT vif_plugging_timeout 300
crudini --set $cfg DEFAULT novncproxy_base_url http://${PUBLIC_IP}:6080/vnc_auto.html
crudini --set $cfg DEFAULT vncserver_listen 0.0.0.0
crudini --set $cfg DEFAULT vncserver_proxyclient_address ${PUBLIC_IP}
crudini --set $cfg DEFAULT vnc_enabled True
crudini --set $cfg DEFAULT volume_api_class nova.volume.cinder.API
crudini --set $cfg DEFAULT image_service nova.image.glance.GlanceImageService
crudini --set $cfg DEFAULT osapi_volume_listen 0.0.0.0

# configure logging to stderr
crudini --del $cfg DEFAULT log_dir
crudini --set $cfg DEFAULT log_file ""
crudini --set $cfg DEFAULT use_stderr True
crudini --set $cfg DEFAULT admin_token "${KEYSTONE_ADMIN_TOKEN}"

crudini --set $cfg conductor workers 8

if [ "${NETWORK_MANAGER}" == "nova" ] ; then
  crudini --set $cfg DEFAULT network_manager nova.network.manager.FlatDHCPManager
  crudini --set $cfg DEFAULT firewall_driver nova.virt.libvirt.firewall.IptablesFirewallDriver
  crudini --set $cfg DEFAULT network_size 254
  crudini --set $cfg DEFAULT allow_same_net_traffic False
  crudini --set $cfg DEFAULT multi_host True
  crudini --set $cfg DEFAULT send_arp_for_ha True
  crudini --set $cfg DEFAULT share_dhcp_address True
  crudini --set $cfg DEFAULT force_dhcp_release True
  crudini --set $cfg DEFAULT flat_interface $FLAT_INTERFACE
  crudini --set $cfg DEFAULT flat_network_bridge br100
  crudini --set $cfg DEFAULT public_interface $PUBLIC_INTERFACE
elif [ "${NETWORK_MANAGER}" == "neutron" ] ; then
  check_required_vars NEUTRON_SHARED_SECRET
  crudini --set $cfg DEFAULT service_neutron_metadata_proxy True
  crudini --set $cfg DEFAULT neutron_metadata_proxy_shared_secret ${NEUTRON_SHARED_SECRET}
  crudini --set $cfg DEFAULT neutron_default_tenant_id default
  crudini --set $cfg DEFAULT network_api_class nova.network.neutronv2.api.API
  crudini --set $cfg DEFAULT security_group_api neutron
  crudini --set $cfg DEFAULT firewall_driver nova.virt.firewall.NoopFirewallDriver
else
  echo "Incorrect NETWORK_MANAGER ${NETWORK_MANAGER}. Supported options are nova and neutron."
  exit 1
fi

# disabled pending answers to http://lists.openstack.org/pipermail/openstack/2014-October/009997.html
#for option in auth_protocol auth_host auth_port; do
#    crudini --del $cfg \
#        keystone_authtoken \
#        $option
#done

crudini --set $cfg keystone_authtoken auth_uri "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/"
crudini --set $cfg keystone_authtoken auth_protocol http
crudini --set $cfg keystone_authtoken auth_host ${KEYSTONE_PUBLIC_SERVICE_HOST}
crudini --set $cfg keystone_authtoken auth_port 5000

crudini --set $cfg keystone_authtoken admin_user ${NOVA_KEYSTONE_USER}
crudini --set $cfg keystone_authtoken admin_password "${NOVA_KEYSTONE_PASSWORD}"
crudini --set $cfg keystone_authtoken admin_tenant_name ${ADMIN_TENANT_NAME}

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
export OS_USERNAME="${NOVA_KEYSTONE_USER}"
export OS_PASSWORD="${NOVA_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

# Configure database connection
crudini --set $cfg \
    database \
    connection \
    "mysql://${NOVA_DB_USER}:${NOVA_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${NOVA_DB_NAME}"
