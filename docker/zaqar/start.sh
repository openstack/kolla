#!/bin/sh

set -e

. /opt/kolla/kolla-common.sh

: ${ADMIN_TENANT_NAME:=admin}
: ${ZAQAR_KEYSTONE_USER:=zaqar}
: ${KEYSTONE_AUTH_PROTOCOL:=http}

check_required_vars ZAQAR_KEYSTONE_PASSWORD ZAQAR_SERVER_SERVICE_HOST \
                    KEYSTONE_ADMIN_SERVICE_HOST KEYSTONE_ADMIN_TOKEN \
                    PUBLIC_IP
dump_vars

#check_for_mongodb
check_for_keystone

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
export OS_USERNAME="${ZAQAR_KEYSTONE_USER}"
export OS_PASSWORD="${ZAQAR_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

cfg=/etc/zaqar/zaqar.conf

crudini --set $cfg DEFAULT log_file \
    ""
crudini --set $cfg DEFAULT use_stderr \
    true

crudini --set $cfg drivers storage \
    sqlite

crudini --set $cfg keystone_authtoken admin_password \
    "${ZAQAR_KEYSTONE_PASSWORD}"
crudini --set $cfg keystone_authtoken admin_user \
    "${ZAQAR_KEYSTONE_USER}"
crudini --set $cfg  keystone_authtoken admin_tenant_name \
    "${ADMIN_TENANT_NAME}"
crudini --set $cfg keystone_authtoken auth_uri \
    "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
crudini --set $cfg keystone_authtoken auth_protocol \
    "${KEYSTONE_AUTH_PROTOCOL}"
crudini --set $cfg keystone_authtoken auth_host \
    "${KEYSTONE_PUBLIC_SERVICE_HOST}"
crudini --set $cfg keystone_authtoken auth_port \
    5000


export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"
crux user-create -n ${ZAQAR_KEYSTONE_USER} \
    -p ${ZAQAR_KEYSTONE_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r admin

crux endpoint-create --remove-all -n ${ZAQAR_KEYSTONE_USER} -t messaging \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${ZAQAR_SERVER_SERVICE_HOST}:8888" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${PUBLIC_IP}:8888" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${ZAQAR_SERVER_SERVICE_HOST}:8888"

exec /usr/bin/zaqar-server
