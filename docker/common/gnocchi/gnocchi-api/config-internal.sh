#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-gnocchi.sh

check_required_vars KEYSTONE_ADMIN_TOKEN \
                    KEYSTONE_AUTH_PROTOCOL \
                    KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_SERVICE_PORT \
                    ADMIN_TENANT_NAME \
                    GNOCCHI_DB_NAME \
                    GNOCCHI_DB_USER \
                    GNOCCHI_DB_PASSWORD \
                    GNOCCHI_SERVICE_PROTOCOL \
                    GNOCCHI_SERVICE_PORT \
                    GNOCCHI_ARCHIVE_POLICY \
                    GNOCCHI_STORAGE_BACKEND \
                    GNOCCHI_KEYSTONE_USER \
                    GNOCCHI_ADMIN_PASSWORD \
                    GNOCCHI_API_SERVICE_HOST

fail_unless_os_service_running keystone
fail_unless_db

mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${GNOCCHI_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${GNOCCHI_DB_NAME}.* TO
       '${GNOCCHI_DB_USER}'@'%' IDENTIFIED BY '${GNOCCHI_DB_PASSWORD}'

EOF


export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"


crux user-create -n ${GNOCCHI_KEYSTONE_USER} \
    -p ${GNOCCHI_ADMIN_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r service

crux service-create -n ${GNOCCHI_KEYSTONE_USER} -t "metric" \
    -d "OpenStack Metric Service"

crux endpoint-create i--remove-all -n ${GNOCCHI_KEYSTONE_USER} -t metric \
    -I "${GNOCCHI_SERVICE_PROTOCOL}://${GNOCCHI_API_SERVICE_HOST}:${GNOCCHI_SERVICE_PORT}" \
    -P "${GNOCCHI_SERVICE_PROTOCOL}://${GNOCCHI_API_SERVICE_HOST}:${GNOCCHI_SERVICE_PORT}" \
    -A "${GNOCCHI_SERVICE_PROTOCOL}://${GNOCCHI_API_SERVICE_HOST}:${GNOCCHI_SERVICE_PORT}"

exec /usr/bin/gnocchi-api
