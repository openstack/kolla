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
: ${PUBLIC_IP:=$MY_IP}

if ! [ "$GLANCE_DB_PASSWORD" ]; then
    GLANCE_DB_PASSWORD=$(openssl rand -hex 15)
    export GLANCE_DB_PASSWORD
fi

if ! [ "$GLANCE_KEYSTONE_PASSWORD" ]; then
    GLANCE_KEYSTONE_PASSWORD=$(openssl rand -hex 15)
    export GLANCE_KEYSTONE_PASSWORD
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
        DEFAULT \
        bind_host \
        $MY_IP
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

