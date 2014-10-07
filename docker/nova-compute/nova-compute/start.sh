#!/bin/sh

: ${NOVA_DB_USER:=nova}
: ${NOVA_DB_NAME:=nova}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${NOVA_KEYSTONE_USER:=nova}
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

mysql -h ${MARIADB_PORT_3306_TCP_ADDR} -u root \
	-p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${NOVA_DB_NAME};
GRANT ALL PRIVILEGES ON nova* TO
	'${NOVA_DB_USER}'@'%' IDENTIFIED BY '${NOVA_DB_PASSWORD}'
EOF

crudini --set /etc/nova/nova database connection \
    "mysql://nova:${NOVA_DB_PASSWORD}@${MARIADB_PORT_3306_TCP_ADDR}:${MARIADB_PORT_3306_TCP_PORT}/nova"
crudini --set /etc/nova/nova DEFAULT admin_token "${KEYSTONE_ADMIN_TOKEN}"
crudini --del /etc/nova/nova DEFAULT log_file
crudini --del /etc/nova/nova  DEFAULT log_dir
crudini --set /etc/nova/nova DEFAULT use_stderr True
crudini --set /etc/keystone/keystone.conf libvirt connection_uri qemu+tcp://${NOVA_PORT_16509_TCP_PORT}/system

/usr/bin/nova-manage db_sync

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_PORT_35357_TCP_ADDR}:35357/v2.0"

/usr/bin/keystone user-create --name ${NOVA_KEYSTONE_USER} --pass ${NOVA_ADMIN_PASSWORD}
/usr/bin/keystone role-create --name ${NOVA_KEYSTONE_USER}
/usr/bin/keystone user-role-add --user ${NOVA_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}

exec /usr/bin/nova-compute
