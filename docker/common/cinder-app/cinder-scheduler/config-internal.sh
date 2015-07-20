#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-cinder.sh

fail_unless_db

check_required_vars CINDER_DB_NAME \
                    CINDER_DB_PASSWORD \
                    CINDER_DB_USER \
                    DB_ROOT_PASSWORD \
                    INIT_CINDER_DB \
                    MARIADB_SERVICE_HOST

cfg=/etc/cinder/cinder.conf

if [ "${INIT_CINDER_DB}" == "true" ]; then
    mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${CINDER_DB_NAME};
GRANT ALL PRIVILEGES ON ${CINDER_DB_NAME}.* TO
'${CINDER_DB_USER}'@'%' IDENTIFIED BY '${CINDER_DB_PASSWORD}'
EOF

    su -s /bin/sh -c "cinder-manage db sync" cinder
fi

crudini --set $cfg \
    DEFAULT \
    log_file \
    "${CINDER_SCHEDULER_LOG_FILE}"

echo "Starting cinder-scheduler"
exec /usr/bin/cinder-scheduler --config-file $cfg
