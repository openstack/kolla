#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-magnum.sh

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    MAGNUM_KEYSTONE_USER MAGNUM_KEYSTONE_PASSWORD \
                    KEYSTONE_AUTH_PROTOCOL ADMIN_TENANT_NAME \
                    MAGNUM_API_SERVICE_HOST KEYSTONE_ADMIN_SERVICE_PORT \
                    MAGNUM_API_SERVICE_PORT

fail_unless_os_service_running keystone

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"
crux user-create -n ${MAGNUM_KEYSTONE_USER} \
    -p ${MAGNUM_KEYSTONE_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r admin

crux endpoint-create --remove-all -n ${MAGNUM_KEYSTONE_USER} -t container \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${MAGNUM_API_SERVICE_HOST}:${MAGNUM_API_SERVICE_PORT}/v1" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${MAGNUM_API_SERVICE_HOST}:${MAGNUM_API_SERVICE_PORT}/v1" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${MAGNUM_API_SERVICE_HOST}:${MAGNUM_API_SERVICE_PORT}/v1"

exec /usr/bin/magnum-api
