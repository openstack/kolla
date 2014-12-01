#!/bin/sh

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-ceilometer.sh

check_required_vars CEILOMETER_DB_USER CEILOMETER_DB_NAME \
                    CEILOMETER_DB_PASSWORD KEYSTONE_ADMIN_TOKEN \
                    KEYSTONE_AUTH_PROTOCOL KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_SERVICE_PORT ADMIN_TENANT_NAME \
                    CEILOMETER_KEYSTONE_USER CEILOMETER_ADMIN_PASSWORD \
                    CEILOMETER_API_SERVICE_HOST PUBLIC_IP

check_for_keystone
check_for_db

#TODO(pkilambi): Add mongodb support

mysql -h ${MARIADB_SERVICE_HOST} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${CEILOMETER_DB_NAME} DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON ${CEILOMETER_DB_NAME}.* TO
       '${CEILOMETER_DB_USER}'@'%' IDENTIFIED BY '${CEILOMETER_DB_PASSWORD}'

EOF


export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"


crux user-create -n ${CEILOMETER_KEYSTONE_USER} \
    -p ${CEILOMETER_ADMIN_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r admin

crux service-create -n ${CEILOMETER_KEYSTONE_USER} -t metering \
    -d "Ceilometer Telemetry Service"

crux endpoint-create i--remove-all -n ${CEILOMETER_KEYSTONE_USER} -t metering \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${CEILOMETER_API_SERVICE_HOST}:8777" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${PUBLIC_IP}:8777" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${CEILOMETER_API_SERVICE_HOST}:8777"

cfg=/etc/ceilometer/ceilometer.conf
crudini --set $cfg \
    DEFAULT connection
    "mysql://${CEILOMETER_DB_USER}:${CEILOMETER_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${CEILOMETER_DB_NAME}"


exec /usr/bin/ceilometer-api
