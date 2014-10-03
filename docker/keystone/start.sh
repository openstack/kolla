#!/bin/bash

# Exit the container if MariaDB is not yet up - then depend on kube to restart
if [ -z "$MARIADBMASTER_PORT_3306_TCP_PORT" ]; then
        exit 1
fi

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

# TODO(sdake) better would be to retry each keystone operation
/usr/bin/sleep 5

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://127.0.0.1:35357/v2.0"

# Create the admin user
/usr/bin/keystone user-create --name admin --pass ${KEYSTONE_ADMIN_PASSWORD}
/usr/bin/keystone role-create --name admin
/usr/bin/keystone tenant-create --name ${ADMIN_TENANT_NAME}
/usr/bin/keystone user-role-add --user admin --role admin --tenant ${ADMIN_TENANT_NAME}

# Create the keystone service and endpoint
/usr/bin/keystone service-create --name=keystone --type=identity --description="Identity Service"
export SERVICE_ENDPOINT_USER="http://${KEYSTONEMASTER_PORT_5000_TCP_ADDR}:5000/v2.0"
export SERVICE_ENDPOINT_ADMIN="http://${KEYSTONEMASTER_PORT_35357_TCP_ADDR}:35357/v2.0"
/usr/bin/keystone endpoint-create \
 --region RegionOne \
 --service-id=`keystone service-list | grep keystone | tr -s ' ' | cut -d \  -f 2` \
 --publicurl=${SERVICE_ENDPOINT_USER} \
 --internalurl=${SERVICE_ENDPOINT_USER} \
 --adminurl=http:${SERVICE_ENDPOINT_ADMIN}


# TODO(sdake) better would be to validate the database for the endpoint
/usr/bin/sleep 5

kill -TERM $PID

# TODO(sdake) better here would be to check ps for the existance of $PID
/usr/bin/sleep 2

echo "Running keystone service."
exec /usr/bin/keystone-all
