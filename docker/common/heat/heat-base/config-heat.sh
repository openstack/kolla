#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh

check_required_vars HEAT_API_CFN_SERVICE_PORT \
                    HEAT_API_CFN_URL_HOST \
                    HEAT_DB_PASSWORD \
                    HEAT_DOMAIN_PASS \
                    HEAT_KEYSTONE_PASSWORD \
                    KEYSTONE_PUBLIC_SERVICE_HOST \
                    KEYSTONE_PUBLIC_SERVICE_PORT \
                    MARIADB_SERVICE_HOST \
                    RABBITMQ_SERVICE_HOST

fail_unless_db
dump_vars

# this should use the keystone admin port
# https://bugs.launchpad.net/kolla/+bug/1469209
cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:\
${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
export OS_USERNAME="${HEAT_KEYSTONE_USER}"
export OS_PASSWORD="${HEAT_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

crudini --set /etc/heat/heat.conf DEFAULT log_file \
    ""
crudini --set /etc/heat/heat.conf DEFAULT use_stderr \
    true
crudini --set /etc/heat/heat.conf DEFAULT rpc_backend \
    heat.openstack.common.rpc.impl_kombu
crudini --set /etc/heat/heat.conf DEFAULT rabbit_host \
    "${RABBITMQ_SERVICE_HOST}"
crudini --set /etc/heat/heat.conf DEFAULT rabbit_userid \
    "${RABBIT_USER}"
crudini --set /etc/heat/heat.conf DEFAULT rabbit_password \
    "${RABBIT_PASSWORD}"

crudini --set /etc/heat/heat.conf database connection \
    mysql://${HEAT_DB_USER}:${HEAT_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${HEAT_DB_NAME}

crudini --set /etc/heat/heat.conf keystone_authtoken auth_protocol \
    "${KEYSTONE_AUTH_PROTOCOL}"
crudini --set /etc/heat/heat.conf keystone_authtoken auth_host \
    "${KEYSTONE_PUBLIC_SERVICE_HOST}"
crudini --set /etc/heat/heat.conf keystone_authtoken auth_port \
    "${KEYSTONE_PUBLIC_SERVICE_PORT}"
crudini --set /etc/heat/heat.conf keystone_authtoken auth_uri \
    "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
crudini --set /etc/heat/heat.conf  keystone_authtoken admin_tenant_name \
    "${ADMIN_TENANT_NAME}"
crudini --set /etc/heat/heat.conf keystone_authtoken admin_user \
    "${HEAT_KEYSTONE_USER}"
crudini --set /etc/heat/heat.conf keystone_authtoken admin_password \
    "${HEAT_KEYSTONE_PASSWORD}"

crudini --set /etc/heat/heat.conf ec2authtoken auth_uri \
    "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"

crudini --set /etc/heat/heat.conf DEFAULT heat_metadata_server_url \
    http://${HEAT_API_CFN_URL_HOST}:${HEAT_API_CFN_SERVICE_PORT}
crudini --set /etc/heat/heat.conf DEFAULT heat_waitcondition_server_url \
    http://${HEAT_API_CFN_URL_HOST}:${HEAT_API_CFN_SERVICE_PORT}/v1/waitcondition

crudini --set /etc/heat/heat.conf DEFAULT stack_domain_admin \
    "heat_domain_admin"
crudini --set /etc/heat/heat.conf DEFAULT stack_domain_admin_password \
    "${HEAT_DOMAIN_PASS}"
crudini --set /etc/heat/heat.conf DEFAULT stack_user_domain_name \
    "heat_user_domain"
