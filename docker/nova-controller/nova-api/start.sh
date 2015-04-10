#!/bin/sh

set -e

. /opt/kolla/config-nova.sh

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    NOVA_KEYSTONE_USER NOVA_KEYSTONE_PASSWORD \
                    ADMIN_TENANT_NAME NOVA_API_SERVICE_HOST \
                    NOVA_EC2_API_SERVICE_HOST PUBLIC_IP NOVA_DB_NAME
fail_unless_os_service_running keystone
fail_unless_db $NOVA_DB_NAME

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

cfg=/etc/nova/nova.conf

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_API_LOG_FILE}"

crux user-create --update \
    -n "${NOVA_KEYSTONE_USER}" \
    -p "${NOVA_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

crux endpoint-create --remove-all \
    -n ec2 -t ec2 \
    -I "http://${NOVA_EC2_API_SERVICE_HOST}:8773/services/Cloud" \
    -P "http://${PUBLIC_IP}:8773/services/Cloud" \
    -A "http://${NOVA_EC2_API_SERVICE_HOST}:8773/services/Admin"

crux endpoint-create --remove-all \
    -n nova -t compute \
    -I "http://${NOVA_API_SERVICE_HOST}:8774/v2/\$(tenant_id)s" \
    -P "http://${PUBLIC_IP}:8774/v2/\$(tenant_id)s" \
    -A "http://${NOVA_API_SERVICE_HOST}:8774/v2/\$(tenant_id)s"

crux endpoint-create --remove-all \
    -n novav3 -t computev3 \
    -I "http://${NOVA_API_SERVICE_HOST}:8774/v3" \
    -P "http://${PUBLIC_IP}:8774/v3" \
    -A "http://${NOVA_API_SERVICE_HOST}:8774/v3"

exec /usr/bin/nova-api
