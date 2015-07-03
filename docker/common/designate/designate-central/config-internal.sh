#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-designate.sh

check_required_vars MARIADB_SERVICE_HOST DB_ROOT_PASSWORD DESIGNATE_DB_NAME \
                    DESIGNATE_DB_USER DESIGNATE_DB_PASSWORD INIT_DESIGNATE_DB

fail_unless_db

CONF=/etc/designate/designate.conf

if [ "${INIT_DESIGNATE_DB}" == "true" ]; then
    echo "Configuring database"
    mysql -h ${MARIADB_SERVICE_HOST} -u root -p"${DB_ROOT_PASSWORD}" mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${DESIGNATE_DB_NAME};
GRANT ALL PRIVILEGES ON ${DESIGNATE_DB_NAME}.* TO '${DESIGNATE_DB_USER}'@'%' IDENTIFIED BY '${DESIGNATE_DB_PASSWORD}'
EOF

    designate-manage database sync
fi

exec /usr/bin/designate-central
