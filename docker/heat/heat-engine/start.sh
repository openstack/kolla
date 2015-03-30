#!/bin/sh

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-heat.sh

check_required_vars HEAT_DB_NAME HEAT_DB_USER HEAT_DB_PASSWORD
fail_unless_db

mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${HEAT_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${HEAT_DB_NAME}.* TO
    '${HEAT_DB_USER}'@'%' IDENTIFIED BY '${HEAT_DB_PASSWORD}'
EOF

/usr/bin/heat-manage db_sync

exec /usr/bin/heat-engine
