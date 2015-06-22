#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-glance.sh

check_required_vars GLANCE_DB_NAME GLANCE_DB_USER GLANCE_DB_PASSWORD \
                    INIT_GLANCE_DB
# lets wait for the DB to be available
wait_for 25 1 check_for_db

if [ "${INIT_GLANCE_DB}" == "true" ]; then
    mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${GLANCE_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${GLANCE_DB_NAME}.* TO
       '${GLANCE_DB_USER}'@'%' IDENTIFIED BY '${GLANCE_DB_PASSWORD}'

EOF

    /usr/bin/glance-manage db_sync
fi

exec /usr/bin/glance-registry
