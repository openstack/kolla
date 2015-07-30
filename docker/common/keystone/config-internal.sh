#!/bin/bash

set -e

# Run Kolla common script
echo "Running the kolla-common script"
. /opt/kolla/kolla-common.sh

## Check DB connectivity and required variables
echo "Checking connectivity to the DB"
fail_unless_db
echo "Checking for required variables"
check_required_vars ADMIN_TENANT_NAME \
                    INIT_KEYSTONE_DB \
                    KEYSTONE_ADMIN_PASSWORD \
                    KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_TOKEN \
                    KEYSTONE_DB_PASSWORD \
                    KEYSTONE_PUBLIC_SERVICE_HOST \
                    PUBLIC_IP

dump_vars

# Setup the Keystone DB
echo "Setting up Keystone DB"
mysql -h ${MARIADB_SERVICE_HOST} -u root -p"${DB_ROOT_PASSWORD}" mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${KEYSTONE_DB_NAME};
GRANT ALL PRIVILEGES ON ${KEYSTONE_DB_NAME}.* TO
    '${KEYSTONE_DB_USER}'@'%' IDENTIFIED BY '${KEYSTONE_DB_PASSWORD}'
EOF

# File path and name used by crudini tool
cfg=/etc/keystone/keystone.conf

# Token Configuration
echo "Configuring keystone.conf"
crudini --set $cfg \
    DEFAULT \
    admin_token \
    "${KEYSTONE_ADMIN_TOKEN}"

# Database Configuration
crudini --set $cfg \
    database \
    connection \
    "mysql://${KEYSTONE_DB_USER}:${KEYSTONE_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${KEYSTONE_DB_NAME}"

# Logging
crudini --del $cfg \
    DEFAULT \
    log_dir
crudini --set $cfg \
    DEFAULT \
    log_file \
    ${LOG_FILE}
crudini --set $cfg \
    DEFAULT \
    verbose \
    ${VERBOSE_LOGGING}
crudini --set $cfg \
    DEFAULT \
    debug \
    ${DEBUG_LOGGING}
crudini --set $cfg \
    DEFAULT \
    use_stderr \
    ${USE_STDERR}

# Token Management
crudini --set $cfg \
    token \
    provider \
    keystone.token.providers."${TOKEN_PROVIDER}".Provider
crudini --set $cfg \
    token \
    driver \
    keystone.token.persistence.backends."${TOKEN_DRIVER}".Token
crudini --set $cfg \
    revoke \
    driver \
    keystone.contrib.revoke.backends."${TOKEN_DRIVER}".Revoke

# Setup the openrc auth file
cat > /openrc <<EOF
export OS_AUTH_URL=http://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v${KEYSTONE_API_VERSION}
export OS_USERNAME=${KEYSTONE_USER}
export OS_PASSWORD=${KEYSTONE_ADMIN_PASSWORD}
export OS_TENANT_NAME=${ADMIN_TENANT_NAME}
EOF

# Run PKI Setup script
echo "Setting up PKI"
/usr/bin/keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

# Fix permissions
chown -R keystone:keystone /var/log/keystone
chown -R keystone:keystone /etc/keystone/ssl
chmod -R o-rwx /etc/keystone/ssl

# Initialize the Keystone DB
echo "Initializing Keystone DB"
if [ "${INIT_KEYSTONE_DB}" == "true" ] ; then
    su -s /bin/bash -c "keystone-manage db_sync" keystone
fi

# Start Keystone
echo "Starting Keystone"
/usr/sbin/httpd -DFOREGROUND &
PID=$!

# Export Keystone service environment variables
export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v${KEYSTONE_API_VERSION}"

# Check to make sure the service is running
echo "Verifying Keystone is running"
while ! curl -o /dev/null -s --fail ${SERVICE_ENDPOINT}; do
    echo "waiting for Keystone @ ${SERVICE_ENDPOINT}"
    sleep 1;
done
echo "keystone is active @ ${SERVICE_ENDPOINT}"

# Create Keystone tenant, user, role, service and endpoints
echo "Creating Keystone tenant, user, role, service and endpoints"
crux user-create --update \
    -n ${ADMIN_USER} -p "${ADMIN_USER_PASSWORD}" \
    -t ${ADMIN_TENANT_NAME} -r admin
crux user-create --update \
    -n ${KEYSTONE_USER} -p "${KEYSTONE_ADMIN_PASSWORD}" \
    -t ${ADMIN_TENANT_NAME} -r admin
crux endpoint-create --remove-all \
    -n keystone -t identity \
    -I "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v${KEYSTONE_API_VERSION}" \
    -A "http://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v${KEYSTONE_API_VERSION}" \
    -P "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v${KEYSTONE_API_VERSION}"

# Wait on all jobs to exit before proceeding (see man wait)
wait
