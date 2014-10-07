#!/bin/sh

: ${SWIFT_DB_USER:=swift}
: ${SWIFT_DB_NAME:=swift}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${SWIFT_KEYSTONE_USER:=swift}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
	echo "*** Missing KEYSTONE_ADMIN_TOKEN" >&2
	exit 1
fi

if ! [ "$DB_ROOT_PASSWORD" ]; then
	echo "*** Missing DB_ROOT_PASSWORD" >&2
	exit 1
fi

if ! [ "$SWIFT_DB_PASSWORD" ]; then
	SWIFT_DB_PASSWORD=$(openssl rand -hex 15)
	export SWIFT_DB_PASSWORD
fi

sh /opt/swift/config-swift.sh container

mysql -h ${MARIADB_PORT_3306_TCP_ADDR} -u root \
	-p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${SWIFT_DB_NAME};
GRANT ALL PRIVILEGES ON swift* TO
	'${SWIFT_DB_USER}'@'%' IDENTIFIED BY '${SWIFT_DB_PASSWORD}'
EOF

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_PORT_35357_TCP_ADDR}:35357/v2.0"

/bin/keystone user-create --name ${SWIFT_KEYSTONE_USER} --pass ${SWIFT_ADMIN_PASSWORD}
/bin/keystone role-create --name ${SWIFT_KEYSTONE_USER}
/bin/keystone user-role-add --user ${SWIFT_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}

exec /usr/bin/swift-container-server
