#!/bin/sh

set -e

. /opt/kolla/kolla-common.sh

: ${ADMIN_TENANT_NAME:=admin}
: ${NEUTRON_DB_NAME:=neutron}
: ${NEUTRON_DB_USER:=neutron}
: ${NEUTRON_KEYSTONE_USER:=neutron}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${RABBIT_HOST:=$RABBITMQ_SERVICE_HOST}
: ${RABBIT_USER:=guest}
: ${RABBIT_PASSWORD:=guest}

check_required_vars NEUTRON_KEYSTONE_PASSWORD
dump_vars

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
export OS_USERNAME="${NEUTRON_KEYSTONE_USER}"
export OS_PASSWORD="${NEUTRON_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

# Rabbit
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        rabbit_host \
        "${RABBIT_HOST}"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        rabbit_userid \
        "${RABBIT_USER}"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        rabbit_password \
        "${RABBIT_PASSWORD}"

# Keystone
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        auth_strategy \
        "keystone"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        auth_protocol \
        "${KEYSTONE_AUTH_PROTOCOL}"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        auth_host \
        "${KEYSTONE_ADMIN_SERVICE_HOST}"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        auth_port \
        "${KEYSTONE_ADMIN_SERVICE_PORT}"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        auth_uri \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        admin_tenant_name \
        "${ADMIN_TENANT_NAME}"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        admin_user \
        "${NEUTRON_KEYSTONE_USER}"
crudini --set /etc/neutron/neutron.conf \
        keystone_authtoken \
        admin_password \
        "${NEUTRON_KEYSTONE_PASSWORD}"

# ML2
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        core_plugin \
        "ml2"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        service_plugins \
        "router"
crudini --set /etc/neutron/neutron.conf \
        DEFAULT \
        allow_overlapping_ips \
        "True"

