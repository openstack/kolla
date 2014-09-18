#!/bin/bash

: ${GLANCE_DB_USER:=glance}
: ${GLANCE_DB_NAME:=glance}
: ${KEYSTONE_ADMIN_PASSWORD:=redhat}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
	echo "*** Missing KEYSTONE_ADMIN_TOKEN."
	exit 1
fi

if ! [ "$GLANCE_DB_PASSWORD" ]; then
	GLANCE_DB_PASSWORD=$(openssl rand -hex 15)
fi

if ! [ "$GLANCE_KEYSTONE_PASSWORD" ]; then
	GLANCE_KEYSTONE_PASSWORD=$(openssl rand -hex 15)
fi

mysql -h ${MARIADBMASTER_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS glance;
GRANT ALL PRIVILEGES ON glance* TO
	'glance'@'%' IDENTIFIED BY '${GLANCE_DB_PASSWORD}'
EOF

for service in api registry; do
        crudini --set /etc/glance/glance-$service \
                database \
                connection \
                mysql://${GLANCE_DB_USER}:${GLANCE_DB_PASSWORD}@${MARIADBMASTER_PORT_3306_TCP_ADDR}/${GLANCE_DB_NAME}

	crudini --set /etc/glance/glance-$service \
		keystone_authtoken \
		admin_password \
		"$GLANCE_KEYSTONE_PASSWORD"

	crudini --set /etc/glance/glance-$service \
		keystone_authtoken \
		auth_uri \
		"http://${KEYSTONEMASTER_5000_PORT_5000_TCP_ADDR}:5000/"

	for option in auth_host auth_port auth_protocol; do
		crudini --del /etc/glance/glance-$service \
			keystone_authtoken \
			$optoin
	done
done

/usr/bin/glance-manage db sync

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${KEYSTONEMASTER_35357_PORT_35357_TCP_ADDR}:35357/v2.0"

/bin/keystone user-create --name admin --pass ${KEYSTONE_ADMIN_PASSWORD}
/bin/keystone role-create --name admin
/bin/keystone tenant-create --name admin
/bin/keystone user-role-add --user admin --role admin --tenant admin

exec /usr/bin/glance-api

