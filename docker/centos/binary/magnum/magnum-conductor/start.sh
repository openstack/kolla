#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-magnum.sh

check_required_vars MAGNUM_DB_NAME MAGNUM_DB_USER MAGNUM_DB_PASSWORD
fail_unless_db

mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${MAGNUM_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${MAGNUM_DB_NAME}.* TO
    '${MAGNUM_DB_USER}'@'%' IDENTIFIED BY '${MAGNUM_DB_PASSWORD}'
EOF

/usr/bin/magnum-db-manage upgrade

exec /usr/bin/magnum-conductor
