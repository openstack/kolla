#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh

get_or_create_domain() {
    local DOMAIN_NAME=$1

    DOMAIN_ID=$(designate domain-create --name $DOMAIN_NAME | awk '/id/ { print $4; }')
    # Searching domain if not created
    if [ -z $DOMAIN_ID ]; then
        DOMAIN_ID=$(designate domain-list | awk "/$DOMAIN_NAME/ { print \$2; }")
    fi
    # Fail if domain still don't exist
    if [ -z $DOMAIN_ID ]; then
        echo "Creating domain failed" 1>&2
        exit 1
    fi

    echo $DOMAIN_ID
}

check_required_vars DESIGNATE_DB_PASSWORD DESIGNATE_KEYSTONE_PASSWORD \
                    KEYSTONE_PUBLIC_SERVICE_HOST RABBITMQ_SERVICE_HOST \
                    DESIGNATE_BIND9_RNDC_KEY DESIGNATE_BACKEND \
                    KEYSTONE_PUBLIC_SERVICE_PORT DESIGNATE_KEYSTONE_USER \
                    RABBIT_USERID RABBIT_PASSWORD DESIGNATE_DB_USER \
                    DESIGNATE_DB_NAME KEYSTONE_AUTH_PROTOCOL \
                    KEYSTONE_ADMIN_SERVICE_HOST KEYSTONE_ADMIN_SERVICE_PORT \
                    DEBUG_LOGGING DESIGNATE_POOLMAN_POOLID

fail_unless_db
dump_vars

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
export OS_USERNAME="${DESIGNATE_KEYSTONE_USER}"
export OS_PASSWORD="${DESIGNATE_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

conf=/etc/designate/designate.conf

# Regular configuration.
crudini --set $conf DEFAULT log_file ""
crudini --set $conf DEFAULT use_stderr "True"
crudini --set $conf DEFAULT debug "${DEBUG_LOGGING}"
crudini --set $conf DEFAULT rpc_backend "designate.openstack.common.rpc.impl_kombu"

crudini --set $conf oslo_messaging_rabbit rabbit_host "${RABBITMQ_SERVICE_HOST}"
crudini --set $conf oslo_messaging_rabbit rabbit_userid "${RABBIT_USERID}"
crudini --set $conf oslo_messaging_rabbit rabbit_password "${RABBIT_PASSWORD}"

crudini --set $conf storage:sqlalchemy connection "mysql://${DESIGNATE_DB_USER}:${DESIGNATE_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${DESIGNATE_DB_NAME}"

crudini --set $conf service:api auth_strategy "keystone"
crudini --set $conf service:api api_host "${PUBLIC_IP}"

# Eventhough this is a central-scoped item, it's used in other Designate
# components as well. Thus it should be configured here, from designate-base.
crudini --set $conf service:central default_pool_id "${DESIGNATE_POOLMAN_POOLID}"

crudini --set $conf keystone_authtoken identity_uri "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}"
crudini --set $conf keystone_authtoken auth_uri "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
crudini --set $conf keystone_authtoken admin_tenant_name "${ADMIN_TENANT_NAME}"
crudini --set $conf keystone_authtoken admin_user "${DESIGNATE_KEYSTONE_USER}"
crudini --set $conf keystone_authtoken admin_password "${DESIGNATE_KEYSTONE_PASSWORD}"

if [ "${DESIGNATE_BACKEND}" == "bind9" ]; then
    # Configure a key for RNDC so it can connect with Bind9 to create/delete
    # zones.
    cat > /etc/rndc.key <<EOF
key "rndc-key" {
    algorithm hmac-md5;
    secret "${DESIGNATE_BIND9_RNDC_KEY}";
};
EOF
fi
