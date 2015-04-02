#!/bin/sh

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-glance.sh
: ${GLANCE_API_SERVICE_HOST:=$PUBLIC_IP}

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    GLANCE_KEYSTONE_USER GLANCE_KEYSTONE_PASSWORD \
                    ADMIN_TENANT_NAME GLANCE_API_SERVICE_HOST \
                    PUBLIC_IP

wait_for 30 1 check_for_os_service_running keystone

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

crux user-create --update \
    -n "${GLANCE_KEYSTONE_USER}" \
    -p "${GLANCE_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

crux endpoint-create --remove-all \
    -n glance -t image \
    -I "http://${GLANCE_API_SERVICE_HOST}:9292" \
    -P "http://${PUBLIC_IP}:9292" \
    -A "http://${GLANCE_API_SERVICE_HOST}:9292"

# turn on notification sending by glance
crudini --set /etc/glance/glance-api.conf \
    DEFAULT \
    notification_driver \
    "messaging"

crudini --set /etc/glance/glance-api.conf \
    DEFAULT \
    rabbit_host \
    "${RABBITMQ_SERVICE_HOST}"

crudini --set /etc/glance/glance-api.conf \
    DEFAULT \
    registry_host \
    "${GLANCE_REGISTRY_SERVICE_HOST}"

crudini --set /etc/glance/glance-api.conf \
    DEFAULT \
    debug \
    "True"

exec /usr/bin/glance-api
