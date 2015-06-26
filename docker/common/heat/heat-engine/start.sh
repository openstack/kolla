#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-heat.sh
. /openrc

check_required_vars HEAT_DB_NAME HEAT_DB_USER HEAT_DB_PASSWORD \
                    INIT_HEAT_DB HEAT_DOMAIN_PASS
fail_unless_db

if [ "${INIT_HEAT_DB}" == "true" ]; then
    mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${HEAT_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${HEAT_DB_NAME}.* TO
    '${HEAT_DB_USER}'@'%' IDENTIFIED BY '${HEAT_DB_PASSWORD}'
EOF

    /usr/bin/heat-manage db_sync

    # If the database needs to be created, assume keystone-setup is allowed to
    # run as well.
    heat-keystone-setup-domain \
        --stack-user-domain-name heat_user_domain \
        --stack-domain-admin heat_domain_admin \
        --stack-domain-admin-password ${HEAT_DOMAIN_PASS}
fi

exec /usr/bin/heat-engine
