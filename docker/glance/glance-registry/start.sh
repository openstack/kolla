#!/bin/sh

: ${GLANCE_DB_USER:=glance}
: ${GLANCE_DB_NAME:=glance}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${GLANCE_KEYSTONE_USER:=glance}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
	echo "*** Missing KEYSTONE_ADMIN_TOKEN" >&2
	exit 1
fi

if ! [ "$DB_ROOT_PASSWORD" ]; then
	echo "*** Missing DB_ROOT_PASSWORD" >&2
	exit 1
fi

if ! [ "$GLANCE_DB_PASSWORD" ]; then
	GLANCE_DB_PASSWORD=$(openssl rand -hex 15)
	export GLANCE_DB_PASSWORD
fi

sh /opt/glance/config-glance.sh registry

mysql -h ${MARIADBMASTER_PORT_3306_TCP_ADDR} -u root \
	-p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${GLANCE_DB_NAME};
GRANT ALL PRIVILEGES ON glance* TO
	'${GLANCE_DB_USER}'@'%' IDENTIFIED BY '${GLANCE_DB_PASSWORD}'
EOF

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONEMASTER_35357_PORT_35357_TCP_ADDR}:35357/v2.0"

/bin/keystone user-create --name ${GLANCE_KEYSTONE_USER} --pass ${GLANCE_ADMIN_PASSWORD}
/bin/keystone role-create --name ${GLANCE_KEYSTONE_USER}
/bin/keystone user-role-add --user ${GLANCE_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}

exec /usr/bin/glance-registry
