#!/bin/bash

set -e

. /opt/kolla/config-nova.sh

check_required_vars NOVA_DB_NAME NOVA_DB_USER NOVA_DB_PASSWORD \
                    INIT_NOVA_DB
fail_unless_db

cfg=/etc/nova/nova.conf

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_CONDUCTOR_LOG_FILE}"

if [ "${INIT_NOVA_DB}" == "true" ]; then
    mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${NOVA_DB_NAME};
GRANT ALL PRIVILEGES ON ${NOVA_DB_NAME}.* TO
       '${NOVA_DB_USER}'@'%' IDENTIFIED BY '${NOVA_DB_PASSWORD}'
EOF

    nova-manage db sync
fi

exec /usr/bin/nova-conductor --config-file /etc/nova/nova.conf
