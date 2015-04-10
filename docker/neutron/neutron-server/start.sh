#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh

: ${NEUTRON_FLAT_NETWORK_NAME:=physnet1}
: ${NEUTRON_FLAT_NETWORK_INTERFACE:=eth1}

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_AUTH_PROTOCOL NOVA_API_SERVICE_HOST \
                    NOVA_KEYSTONE_USER NOVA_KEYSTONE_PASSWORD \
                    NEUTRON_DB_NAME NEUTRON_DB_USER NEUTRON_DB_PASSWORD \
                    NEUTRON_KEYSTONE_USER NEUTRON_KEYSTONE_PASSWORD \
                    ADMIN_TENANT_NAME NEUTRON_SERVER_SERVICE_HOST \
                    PUBLIC_IP NEUTRON_DB_PASSWORD
fail_unless_os_service_running keystone
fail_unless_db

mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${NEUTRON_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${NEUTRON_DB_NAME}.* TO
       '${NEUTRON_DB_USER}'@'%' IDENTIFIED BY '${NEUTRON_DB_PASSWORD}'

EOF

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"

# Configure Keystone Service Catalog
crux user-create -n "${NEUTRON_KEYSTONE_USER}" \
    -p "${NEUTRON_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

crux endpoint-create -n neutron -t network \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${NEUTRON_SERVER_SERVICE_HOST}:${NEUTRON_SERVER_SERVICE_PORT}" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${NEUTRON_SERVER_SERVICE_HOST}:${NEUTRON_SERVER_SERVICE_PORT}" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${NEUTRON_SERVER_SERVICE_HOST}:${NEUTRON_SERVER_SERVICE_PORT}"

core_cfg=/etc/neutron/neutron.conf
ml2_cfg=/etc/neutron/plugins/ml2/ml2_conf.ini

# Logging
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        log_file \
        "${NEUTRON_SERVER_LOG_FILE}"

# Database
crudini --set $core_cfg \
        database \
        connection \
        "mysql://${NEUTRON_DB_USER}:${NEUTRON_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${NEUTRON_DB_NAME}"
# Nova
crudini --set $core_cfg \
        DEFAULT \
        notify_nova_on_port_status_changes \
        "True"
crudini --set $core_cfg \
        DEFAULT \
        notify_nova_on_port_data_changes \
        "True"
crudini --set $core_cfg \
        DEFAULT \
        nova_url \
        "http://${NOVA_API_SERVICE_HOST}:${NOVA_API_SERVICE_PORT}/v2"
crudini --set $core_cfg \
        DEFAULT \
        nova_admin_auth_url \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"
crudini --set $core_cfg \
        DEFAULT \
        nova_region_name \
        "${KEYSTONE_REGION}"
crudini --set $core_cfg \
        DEFAULT \
        nova_admin_username \
        "${NOVA_KEYSTONE_USER}"
crudini --set $core_cfg \
        DEFAULT \
        nova_admin_tenant_id \
        "$(keystone tenant-list | grep $ADMIN_TENANT_NAME | awk '{print $2;}')"
crudini --set $core_cfg \
        DEFAULT \
        nova_admin_password \
        "${NOVA_KEYSTONE_PASSWORD}"

if [[ ${MECHANISM_DRIVERS} =~ .*linuxbridge.* ]]; then
  crudini --set $ml2_cfg \
          linux_bridge \
          physical_interface_mappings \
          "${NEUTRON_FLAT_NETWORK_NAME}:${NEUTRON_FLAT_NETWORK_INTERFACE}"
fi

su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade juno" neutron

exec /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
