#!/bin/bash

set -e

: ${KEYSTONE_ADMIN_PASSWORD:=kolla}
: ${ADMIN_TENANT_NAME:=admin}

. /opt/kolla/kolla-common.sh
check_for_db
check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_DB_PASSWORD \
                    KEYSTONE_ADMIN_PASSWORD ADMIN_TENANT_NAME
dump_vars

mysql -h ${MARIADB_SERVICE_HOST} -u root -p"${DB_ROOT_PASSWORD}" mysql <<EOF
CREATE DATABASE IF NOT EXISTS keystone;
GRANT ALL PRIVILEGES ON keystone.* TO
    'keystone'@'%' IDENTIFIED BY '${KEYSTONE_DB_PASSWORD}'
EOF

crudini --set /etc/keystone/keystone.conf \
    database \
    connection \
    "mysql://keystone:${KEYSTONE_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/keystone"
crudini --set /etc/keystone/keystone.conf \
    DEFAULT \
    admin_token \
    "${KEYSTONE_ADMIN_TOKEN}"
crudini --set /etc/keystone/keystone.conf \
    DEFAULT \
    log_file \
    ""
crudini --del /etc/keystone/keystone.conf \
    DEFAULT \
    log_dir
crudini --set /etc/keystone/keystone.conf DEFAULT use_stderr True

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
export OS_USERNAME=admin
export OS_PASSWORD="${KEYSTONE_ADMIN_PASSWORD}"
export OS_TENANT_NAME=${ADMIN_TENANT_NAME}
EOF

/usr/bin/keystone-manage db_sync
/usr/bin/keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

/usr/bin/keystone-all &
PID=$!

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${MY_IP}:35357/v2.0"

while ! curl -o /dev/null -s --fail ${SERVICE_ENDPOINT}; do
    echo "waiting for keystone @ ${SERVICE_ENDPOINT}"
    sleep 1;
done
echo "keystone is active @ ${SERVICE_ENDPOINT}"

crux user-create --update \
    -n admin -p "${KEYSTONE_ADMIN_PASSWORD}" \
    -t admin -r admin
crux endpoint-create --remove-all \
    -n keystone -t identity \
    -I "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0" \
    -A "http://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0" \
    -P "http://${PUBLIC_IP}:5000/v2.0"

kill -TERM $PID

while curl -o /dev/null -s --fail ${SERVICE_ENDPOINT}; do
    echo "waiting for keystone @ ${SERVICE_ENDPOINT} to exit"
    sleep 1;
done

echo "Running keystone service."
exec /usr/bin/keystone-all
