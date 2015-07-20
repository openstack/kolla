#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh

check_required_vars ADMIN_TENANT_NAME \
                    DEBUG_LOGGING \
                    KEYSTONE_AUTH_PROTOCOL \
                    KEYSTONE_PUBLIC_SERVICE_HOST \
                    KEYSTONE_PUBLIC_SERVICE_PORT \
                    MAGNUM_DB_NAME \
                    MAGNUM_DB_PASSWORD \
                    MAGNUM_DB_USER \
                    MAGNUM_KEYSTONE_PASSWORD \
                    MAGNUM_KEYSTONE_USER \
                    RABBITMQ_SERVICE_HOST \
                    VERBOSE_LOGGING

fail_unless_db
dump_vars

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
export OS_USERNAME="${MAGNUM_KEYSTONE_USER}"
export OS_PASSWORD="${MAGNUM_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

cfg=/etc/magnum/magnum.conf

crudini --set $cfg DEFAULT log_file ""
crudini --set $cfg DEFAULT verbose "${VERBOSE_LOGGING}"
crudini --set $cfg DEFAULT debug "${DEBUG_LOGGING}"
crudini --set $cfg DEFAULT use_stderr true
crudini --set $cfg DEFAULT rpc_backend magnum.openstack.common.rpc.impl_kombu
crudini --set $cfg DEFAULT admin_user admin
crudini --set $cfg oslo_messaging_rabbit rabbit_host ${RABBITMQ_SERVICE_HOST}
crudini --set $cfg oslo_messaging_rabbit rabbit_userid ${RABBIT_USER}
crudini --set $cfg oslo_messaging_rabbit rabbit_password ${RABBIT_PASSWORD}
crudini --set $cfg database connection \
    mysql://${MAGNUM_DB_USER}:${MAGNUM_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${MAGNUM_DB_NAME}
crudini --set $cfg keystone_authtoken auth_protocol "${KEYSTONE_AUTH_PROTOCOL}"
crudini --set $cfg keystone_authtoken auth_host "${KEYSTONE_PUBLIC_SERVICE_HOST}"
crudini --set $cfg keystone_authtoken auth_port "${KEYSTONE_PUBLIC_SERVICE_PORT}"
crudini --set $cfg keystone_authtoken auth_uri \
    "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
crudini --set $cfg  keystone_authtoken admin_tenant_name "${ADMIN_TENANT_NAME}"
crudini --set $cfg keystone_authtoken admin_user "${MAGNUM_KEYSTONE_USER}"
crudini --set $cfg keystone_authtoken admin_password \
    "${MAGNUM_KEYSTONE_PASSWORD}"
crudini --set $cfg api host ${MAGNUM_API_SERVICE_HOST}
