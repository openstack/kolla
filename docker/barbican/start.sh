#!/bin/bash

set -e

: ${BARBICAN_DB_USER:=barbican}
: ${BARBICAN_DB_NAME:=barbican}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${BARBICAN_KEYSTONE_USER:=barbican}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
    echo "*** Missing KEYSTONE_ADMIN_TOKEN" >&2
        exit 1
fi

if ! [ "$DB_ROOT_PASSWORD" ]; then
        echo "*** Missing DB_ROOT_PASSWORD" >&2
        exit 1
fi

if ! [ "$BARBICAN_DB_PASSWORD" ]; then
        BARBICAN_DB_PASSWORD=$(openssl rand -hex 15)
        export BARBICAN_DB_PASSWORD
fi

mysql -h ${MARIADB_SERVICE_HOST} -u root -p"${DB_ROOT_PASSWORD}" mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${BARBICAN_DB_NAME};
GRANT ALL PRIVILEGES ON barbican.* TO
    '${BARBICAN_DB_USER}'@'%' IDENTIFIED BY '${BARBICAN_DB_PASSWORD}'
EOF

# config file setup
crudini --set /etc/barbican/barbican-api.conf \
    DEFAULT \
    sql_connection \
    "mysql://${BARBICAN_DB_USER}:${BARBICAN_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${BARBICAN_DB_NAME}"
crudini --set /etc/barbican/barbican-api.conf \
    DEFAULT \
    log_dir \
    "/var/log/barbican/"
crudini --set /etc/barbican/barbican-api.conf \
    DEFAULT \
    log_file \
    "/var/log/barbican/barbican.log"
crudini --set /etc/barbican/barbican-api-paste.ini \
    pipeline:barbican_api \
    pipeline \
    "keystone_authtoken context apiapp"
crudini --set /etc/barbican/barbican-api-paste.ini \
    filter:keystone_authtoken \
    auth_host \
    ${KEYSTONE_ADMIN_SERVICE_HOST}
crudini --set /etc/barbican/barbican-api-paste.ini \
    filter:keystone_authtoken \
    auth_port \
    ${KEYSTONE_ADMIN_SERVICE_PORT}
crudini --set /etc/barbican/barbican-api-paste.ini \
    filter:keystone_authtoken \
    auth_protocol \
    ${KEYSTONE_AUTH_PROTOCOL}
crudini --set /etc/barbican/barbican-api-paste.ini \
    filter:keystone_authtoken \
    admin_tenant_name \
    ${ADMIN_TENANT_NAME}
crudini --set /etc/barbican/barbican-api-paste.ini \
    filter:keystone_authtoken \
    admin_user \
    ${BARBICAN_KEYSTONE_USER}
crudini --set /etc/barbican/barbican-api-paste.ini \
    filter:keystone_authtoken \
    admin_password \
    ${BARBICAN_KEYSTONE_USER}

# create the required keystone entities for barbican
export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"

keystone user-get ${BARBICAN_KEYSTONE_USER} > /dev/null 2>&1 || /bin/keystone user-create --name ${BARBICAN_KEYSTONE_USER} --pass ${BARBICAN_ADMIN_PASSWORD}

keystone role-get observer > /dev/null 2>&1 || /bin/keystone role-create --name observer
keystone role-get creator > /dev/null 2>&1 || /bin/keystone role-create --name creator

keystone user-get ${BARBICAN_KEYSTONE_USER} > /dev/null 2>&1 || /bin/keystone user-role-add --user ${BARBICAN_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}

# launch Barbican using uwsgi
exec uwsgi --master --emperor /etc/barbican/vassals
