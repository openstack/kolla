#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-heat.sh

check_required_vars ADMIN_TENANT_NAME \
                    HEAT_API_SERVICE_HOST \
                    HEAT_KEYSTONE_PASSWORD \
                    HEAT_KEYSTONE_USER \
                    KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_TOKEN \
                    KEYSTONE_AUTH_PROTOCOL \
                    PUBLIC_IP

fail_unless_os_service_running keystone

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"
crux user-create -n ${HEAT_KEYSTONE_USER} \
    -p ${HEAT_KEYSTONE_PASSWORD} \
    -t ${ADMIN_TENANT_NAME} \
    -r admin

crux endpoint-create --remove-all -n ${HEAT_KEYSTONE_USER} -t orchestration \
    -I "${KEYSTONE_AUTH_PROTOCOL}://${HEAT_API_SERVICE_HOST}:8004/v1/%(tenant_id)s" \
    -P "${KEYSTONE_AUTH_PROTOCOL}://${PUBLIC_IP}:8004/v1/%(tenant_id)s" \
    -A "${KEYSTONE_AUTH_PROTOCOL}://${HEAT_API_SERVICE_HOST}:8004/v1/%(tenant_id)s"

# will use crux after https://github.com/larsks/crux/issues/1 is implemented
openstack role list --os-token="${KEYSTONE_ADMIN_TOKEN}" --os-url $SERVICE_ENDPOINT -f csv | tail -n +2 | awk -F, '{print $2}' | grep heat_stack_user || keystone role-create --name heat_stack_user

exec /usr/bin/heat-api
