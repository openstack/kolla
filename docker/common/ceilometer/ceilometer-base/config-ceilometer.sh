#!/bin/bash

set -e
. /opt/kolla/kolla-common.sh

check_required_vars KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_SERVICE_PORT \
                    KEYSTONE_ADMIN_TOKEN \
                    KEYSTONE_PUBLIC_SERVICE_HOST

dump_vars

cat > /openrc <<EOF
export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"
EOF


cfg=/etc/ceilometer/ceilometer.conf

crudini --set $cfg \
    DEFAULT rpc_backend rabbit
crudini --set $cfg \
    DEFAULT rabbit_host ${RABBITMQ_SERVICE_HOST}
crudini --set $cfg \
    DEFAULT rabbit_password ${RABBIT_PASSWORD}

crudini --set $cfg \
    keystone_authtoken \
    auth_uri \
    "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/"
crudini --set $cfg \
    keystone_authtoken \
    admin_tenant_name \
    "${ADMIN_TENANT_NAME}"
crudini --set $cfg \
    keystone_authtoken \
    admin_user \
    "${CEILOMETER_KEYSTONE_USER}"
crudini --set $cfg \
    keystone_authtoken \
    admin_password \
    ${CEILOMETER_ADMIN_PASSWORD}

crudini --set $cfg \
    service_credentials \
    os_auth_url \
    ${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/
crudini --set $cfg \
    service_credentials \
    os_username \
    ceilometer
crudini --set $cfg \
    service_credentials \
    os_tenant_name \
    service
crudini --set $cfg \
    service_credentials \
    os_password \
    ${CEILOMETER_ADMIN_PASSWORD}

crudini --set $cfg \
    publisher
    metering_secret
    ${METERING_SECRET}
