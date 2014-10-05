#!/bin/sh
#
# usage config-glance.sh ( api | registry )

service=$1
cfg=/etc/glance/glance-${service}.conf

: ${GLANCE_DB_USER:=glance}
: ${GLANCE_DB_NAME:=glance}
: ${GLANCE_KEYSTONE_USER:=glance}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$GLANCE_DB_PASSWORD" ]; then
        echo "*** Missing GLANCE_DB_PASSWORD" >&2
        exit 1
fi

crudini --del $cfg \
        DEFAULT \
        log_file \
crudini --set $cfg \
        keystone_authtoken \
        admin_password \
        "${GLANCE_KEYSTONE_PASS}"

for option in auth_protocol auth_host auth_Port; do
        crudini --del $cfg \
        keystone_authtoken \
        $option
done

crudini --set $cfg
        keystone_authtoken \
        auth_uri \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONEMASTER_5000_PORT_5000_TCP_ADDR}:5000/"
crudini --set $cfg
        keystone_authtoken \
        admin_tenant_name \
       "${ADMIN_TENANT_NAME}"
crudini --set $cfg
        keystone_authtoken \
        admin_user \
        "${GLANCE_KEYSTONE_USER}"
crudini --set $cfg
        keystone_authtoken \
        admin_password \
        "${GLANCE_KEYSTONE_PASS}"

crudini --set $cfg \
        database \
        connection \
        "mysql://${GLANCE_DB_USER}:${GLANCE_DB_PASSWORD}@${MARIADB_PORT_3306_TCP_ADDR}:${MARIADB_PORT_3306_TCP_PORT}/${GLANCE_DB_NAME}"

