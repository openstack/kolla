#!/bin/sh

set -e

. /opt/kolla/config-nova-controller.sh

check_for_db

mysql -h ${MARIADB_SERVICE_HOST} -u root \
	-p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${NOVA_DB_NAME};
GRANT ALL PRIVILEGES ON ${NOVA_DB_NAME}.* TO
	'${NOVA_DB_USER}'@'%' IDENTIFIED BY '${NOVA_DB_PASSWORD}'
EOF

nova-manage db sync

exec /usr/bin/nova-conductor
