#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-heat.sh

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    HEAT_CFN_KEYSTONE_USER HEAT_CFN_KEYSTONE_PASSWORD \
                    KEYSTONE_AUTH_PROTOCOL KEYSTONE_ADMIN_SERVICE_PORT \
                    ADMIN_TENANT_NAME HEAT_API_CFN_SERVICE_HOST \
                    HEAT_API_CFN_SERVICE_PORT

fail_unless_os_service_running keystone

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"

crux user-create -n ${HEAT_CFN_KEYSTONE_USER} \
    -p ${HEAT_CFN_KEYSTONE_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r admin

crux endpoint-create --remove-all -n ${HEAT_CFN_KEYSTONE_USER} -t cloudformation \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${HEAT_API_CFN_SERVICE_HOST}:${HEAT_API_CFN_SERVICE_PORT}/v1" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${HEAT_API_CFN_SERVICE_HOST}:${HEAT_API_CFN_SERVICE_PORT}/v1" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${HEAT_API_CFN_SERVICE_HOST}:${HEAT_API_CFN_SERVICE_PORT}/v1"

exec /usr/bin/heat-api-cfn
