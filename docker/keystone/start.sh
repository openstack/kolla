#!/bin/bash

: ${KEYSTONE_ADMIN_PASSWORD:=kolla}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
	KEYSTONE_ADMIN_TOKEN=$(openssl rand -hex 15)
fi

if ! [ "$KEYSTONE_DB_PASSWORD" ]; then
	KEYSTONE_DB_PASSWORD=$(openssl rand -hex 15)
fi

mysql -h ${MARIADBMASTER_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS keystone;
GRANT ALL PRIVILEGES ON keystone.* TO
	'keystone'@'%' IDENTIFIED BY '${KEYSTONE_DB_PASSWORD}'
EOF

crudini --set /etc/keystone/keystone.conf \
	database \
	connection \
	"mysql://keystone:${KEYSTONE_DB_PASSWORD}@${MARIADBMASTER_PORT_3306_TCP_ADDR}:${MARIADBMASTER_PORT_3306_TCP_PORT}/keystone"
crudini --set /etc/keystone/keystone.conf \
	DEFAULT \
	admin_token \
	"${KEYSTONE_ADMIN_TOKEN}"
crudini --del /etc/keystone/keystone.conf \
	DEFAULT \
	log_file
crudini --del /etc/keystone/keystone.conf \
	DEFAULT \
	log_dir
crudini --set /etc/keystone/keystone.conf DEFAULT use_stderr True

cat /etc/keystone/keystone.conf

/usr/bin/keystone-manage db_sync

/usr/bin/keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

/usr/bin/keystone-all &
PID=$!

/bin/sleep 5

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://127.0.0.1:35357/v2.0"

/bin/keystone user-create --name admin --pass ${KEYSTONE_ADMIN_PASSWORD}
/bin/keystone role-create --name admin
/bin/keystone tenant-create --name ${ADMIN_TENANT_NAME}
/bin/keystone user-role-add --user admin --role admin --tenant ${ADMIN_TENANT_NAME}

kill -TERM $PID


echo "Exec-ing keystone-all.."
exec /usr/bin/keystone-all
