#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-designate.sh

CONF=/etc/designate/designate.conf

check_required_vars ADMIN_TENANT_NAME \
                    DESIGNATE_API_SERVICE_HOST \
                    DESIGNATE_API_SERVICE_PORT \
                    DESIGNATE_KEYSTONE_PASSWORD \
                    DESIGNATE_KEYSTONE_USER \
                    KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_SERVICE_PORT \
                    KEYSTONE_AUTH_PROTOCOL \
                    KEYSTONE_ADMIN_TOKEN

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"

fail_unless_os_service_running keystone

crux user-create \
    -n ${DESIGNATE_KEYSTONE_USER} \
    -p ${DESIGNATE_KEYSTONE_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r admin

crux endpoint-create \
    --remove-all \
    -n ${DESIGNATE_KEYSTONE_USER} \
    -t dns \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${DESIGNATE_API_SERVICE_HOST}:${DESIGNATE_API_SERVICE_PORT}/v1" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${DESIGNATE_API_SERVICE_HOST}:${DESIGNATE_API_SERVICE_PORT}/v1" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${DESIGNATE_API_SERVICE_HOST}:${DESIGNATE_API_SERVICE_PORT}/v1"

crudini --set $CONF service:api api_paste_config "/usr/share/designate/api-paste.ini"
crudini --set $CONF service:api api_port "${DESIGNATE_API_SERVICE_PORT}"

exec /usr/bin/designate-api
