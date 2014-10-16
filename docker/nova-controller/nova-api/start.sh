#!/bin/sh

set -e

. /opt/kolla/config-nova-controller.sh

check_for_keystone

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

crux user-create --update \
    -n "${NOVA_KEYSTONE_USER}" \
    -p "${NOVA_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

crux endpoint-create --remove-all \
    -n glance -t image \
    -I "http://${NOVA_API_SERVICE_HOST}:9292" \
    -P "http://${PUBLIC_IP}:9292" \
    -A "http://${NOVA_API_SERVICE_HOST}:9292"

exec /usr/bin/nova-api
