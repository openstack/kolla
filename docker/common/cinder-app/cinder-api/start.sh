#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-cinder.sh

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    ADMIN_TENANT_NAME PUBLIC_IP CINDER_API_SERVICE_HOST \
                    KEYSTONE_AUTH_PROTOCOL KEYSTONE_ADMIN_SERVICE_PORT \
                    CINDER_KEYSTONE_USER CINDER_KEYSTONE_PASSWORD \
                    CINDER_API_SERVICE_LISTEN CINDER_API_SERVICE_PORT

fail_unless_os_service_running keystone

cfg=/etc/cinder/cinder.conf

# Set the auth credentials
export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"

# Create Keystone User
crux user-create --update \
    -n "${CINDER_KEYSTONE_USER}" \
    -p "${CINDER_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

# Configure Keystone
crux endpoint-create --remove-all \
    -n cinder \
    -t volume \
    -P "http://${CINDER_API_SERVICE_HOST}:${CINDER_API_SERVICE_PORT}/v1/\$(tenant_id)s" \
    -A "http://${CINDER_API_SERVICE_HOST}:${CINDER_API_SERVICE_PORT}/v1/\$(tenant_id)s" \
    -I "http://${CINDER_API_SERVICE_HOST}:${CINDER_API_SERVICE_PORT}/v1/\$(tenant_id)s"

crux endpoint-create --remove-all \
    -n cinderv2 \
    -t volumev2 \
    -P "http://${CINDER_API_SERVICE_HOST}:${CINDER_API_SERVICE_PORT}/v2/\$(tenant_id)s" \
    -A "http://${CINDER_API_SERVICE_HOST}:${CINDER_API_SERVICE_PORT}/v2/\$(tenant_id)s" \
    -I "http://${CINDER_API_SERVICE_HOST}:${CINDER_API_SERVICE_PORT}/v2/\$(tenant_id)s"

# Logging
crudini --set $cfg \
        DEFAULT \
        log_file \
        "${CINDER_API_LOG_FILE}"

# API Configuration
crudini --set $cfg \
        DEFAULT \
        osapi_volume_listen \
        "${CINDER_API_SERVICE_LISTEN}"

crudini --set $cfg \
        DEFAULT \
        osapi_volume_listen_port \
        "${CINDER_API_SERVICE_PORT}"

crudini --set $cfg \
        DEFAULT \
        enable_v1_api \
        "true"

crudini --set $cfg \
        DEFAULT \
        enable_v2_api \
        "true"

echo "Starting cinder-api"
exec /usr/bin/cinder-api --config-file $cfg
