#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-neutron.sh

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_AUTH_PROTOCOL NOVA_API_SERVICE_HOST \
                    NOVA_ADMIN_PASSWORD NEUTRON_DB_NAME NEUTRON_DB_USER \
                    NEUTRON_KEYSTONE_USER NEUTRON_KEYSTONE_PASSWORD \
                    ADMIN_TENANT_NAME NEUTRON_SERVER_SERVICE_HOST \
                    PUBLIC_IP NEUTRON_DB_PASSWORD
check_for_keystone
check_for_db

mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${NEUTRON_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${NEUTRON_DB_NAME}.* TO
       '${NEUTRON_DB_USER}'@'%' IDENTIFIED BY '${NEUTRON_DB_PASSWORD}'

EOF

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

# Configure Keystone Service Catalog
crux user-create -n "${NEUTRON_KEYSTONE_USER}" \
    -p "${NEUTRON_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

crux endpoint-create -n neutron -t network \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${NEUTRON_SERVER_SERVICE_HOST}:9696" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${PUBLIC_IP}:9696" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${NEUTRON_SERVER_SERVICE_HOST}:9696"

# Database
crudini --set /etc/neutron/neutron.conf \
        database \
        connection \
        "mysql://${NEUTRON_DB_USER}:${NEUTRON_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${NEUTRON_DB_NAME}"

# Nova
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        notify_nova_on_port_status_changes \
        "True"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        notify_nova_on_port_data_changes \
        "True"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        nova_url \
        "http://${NOVA_API_SERVICE_HOST}:8774/v2"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        nova_admin_auth_url \
        "http://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        nova_region_name \
        "RegionOne"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        nova_admin_username \
        "nova"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        nova_admin_tenant_id \
        "$(keystone tenant-list | grep $ADMIN_TENANT_NAME | awk '{print $2;}')"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        nova_admin_password \
        "${NOVA_ADMIN_PASSWORD}"

/usr/bin/ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

exec /usr/bin/neutron-server
