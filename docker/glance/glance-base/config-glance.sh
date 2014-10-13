#!/bin/sh
#
# usage config-glance.sh ( api | registry )

[ -f /startconfig ] && . /startconfig

MY_IP=$(ip route get $(ip route | awk '$1 == "default" {print $3}') |
    awk '$4 == "src" {print $5}')

: ${ADMIN_TENANT_NAME:=admin}
: ${GLANCE_DB_NAME:=glance}
: ${GLANCE_DB_USER:=glance}
: ${GLANCE_KEYSTONE_USER:=glance}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${PUBLIC_IP:=$GLANCE_API_PORT_9292_TCP_ADDR}

if [ -z "$GLANCE_DB_PASSWORD" ]; then
    echo "ERROR: missing GLANCE_DB_PASSWORD" >&2
    exit 1
fi

if [ -z "$GLANCE_KEYSTONE_PASSWORD" ]; then
    echo "ERROR: missing GLANCE_KEYSTONE_PASSWORD" >&2
    exit 1
fi

if ! [ -f /startconfig ]; then
    cat > /startconfig <<-EOF
ADMIN_TENANT_NAME=${ADMIN_TENANT_NAME}
GLANCE_DB_NAME=${GLANCE_DB_NAME}
GLANCE_DB_USER=${GLANCE_DB_USER}
GLANCE_KEYSTONE_USER=${GLANCE_KEYSTONE_USER}
KEYSTONE_AUTH_PROTOCOL=${KEYSTONE_AUTH_PROTOCOL}
PUBLIC_IP=${PUBLIC_IP}
GLANCE_DB_PASSWORD=${GLANCE_DB_PASSWORD}
GLANCE_KEYSTONE_PASSWORD=${GLANCE_KEYSTONE_PASSWORD}
EOF
fi

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_PORT_5000_TCP_ADDR}:5000/v2.0"
export OS_USERNAME="${GLANCE_KEYSTONE_USER}"
export OS_PASSWORD="${GLANCE_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

for cfg in /etc/glance/glance-api.conf /etc/glance/glance-registry.conf; do
    crudini --del $cfg \
        DEFAULT \
        log_file

    for option in auth_protocol auth_host auth_port; do
        crudini --del $cfg \
            keystone_authtoken \
            $option
    done

    crudini --set $cfg \
        keystone_authtoken \
        auth_uri \
        "http://${KEYSTONE_PUBLIC_PORT_5000_TCP_ADDR}:5000/"
    crudini --set $cfg \
        keystone_authtoken \
        admin_tenant_name \
        "${ADMIN_TENANT_NAME}"
    crudini --set $cfg \
        keystone_authtoken \
        admin_user \
        "${GLANCE_KEYSTONE_USER}"
    crudini --set $cfg \
        keystone_authtoken \
        admin_password \
        "${GLANCE_KEYSTONE_PASSWORD}"

    crudini --set $cfg \
        database \
        connection \
        "mysql://${GLANCE_DB_USER}:${GLANCE_DB_PASSWORD}@${MARIADB_PORT_3306_TCP_ADDR}/${GLANCE_DB_NAME}"
done

