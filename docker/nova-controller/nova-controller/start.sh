#!/bin/sh

: ${NOVA_CONFIG:=nova.conf}
: ${NOVA_DB_USER:=nova}
: ${NOVA_DB_NAME:=nova}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${NOVA_KEYSTONE_USER:=admin}
: ${NOVA_ADMIN_PASSWORD:=kolla}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
	echo "*** Missing KEYSTONE_ADMIN_TOKEN" >&2
	exit 1
fi

if ! [ "$DB_ROOT_PASSWORD" ]; then
	echo "*** Missing DB_ROOT_PASSWORD" >&2
	exit 1
fi

if ! [ "$NOVA_DB_PASSWORD" ]; then
	NOVA_DB_PASSWORD=$(openssl rand -hex 15)
	export NOVA_DB_PASSWORD
fi

while read; do
    LINE="$REPLY"
    /bin/bash $LINE
done < $NOVA_CONFIG

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONEMASTER_35357_PORT_35357_TCP_ADDR}:35357/v2.0"

/usr/bin/keystone user-create --name ${NOVA_KEYSTONE_USER} --pass ${NOVA_ADMIN_PASSWORD}
/usr/bin/keystone role-create --name ${NOVA_KEYSTONE_USER}
/usr/bin/keystone user-role-add --user ${NOVA_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}
