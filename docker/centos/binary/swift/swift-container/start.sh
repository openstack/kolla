#!/bin/bash

: ${SWIFT_DB_USER:=swift}
: ${SWIFT_DB_NAME:=swift}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${SWIFT_KEYSTONE_USER:=swift}
: ${ADMIN_TENANT_NAME:=admin}

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    SWIFT_ADMIN_PASSWORD
fail_unless_db
fail_unless_os_service_running keystone

if ! [ "$SWIFT_DB_PASSWORD" ]; then
	SWIFT_DB_PASSWORD=$(openssl rand -hex 15)
	export SWIFT_DB_PASSWORD
fi

sh /opt/swift/config-swift.sh container

mysql -h ${MARIADB_SERVICE_HOST} -u root \
	-p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${SWIFT_DB_NAME};
GRANT ALL PRIVILEGES ON swift* TO
	'${SWIFT_DB_USER}'@'%' IDENTIFIED BY '${SWIFT_DB_PASSWORD}'
EOF

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

/bin/keystone user-create --name ${SWIFT_KEYSTONE_USER} --pass ${SWIFT_ADMIN_PASSWORD}
/bin/keystone role-create --name ${SWIFT_KEYSTONE_USER}
/bin/keystone user-role-add --user ${SWIFT_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}

exec /usr/bin/swift-container-server
