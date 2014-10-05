#!/bin/sh

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
        echo "*** Missing KEYSTONE_ADMIN_TOKEN" >&2
        exit 1
fi

. /opt/glance/config-glance.sh

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://${KEYSTONE_ADMIN_PORT_35357_TCP_ADDR}:35357/v2.0"

crux user-create -n "${GLANCE_KEYSTONE_USER}" \
	-p "${GLANCE_KEYSTONE_PASSWORD}" \
	-t "${ADMIN_TENANT_NAME}" \
	-r admin

crux endpoint-create -n glance -t image \
	-I "http://${GLANCE_API_PORT_9292_TCP_ADDR}:9292" \
	-P "http://${PUBLIC_IP}:9292" \
	-A "http://${GLANCE_API_PORT_9292_TCP_ADDR}:9292"

exec /usr/bin/glance-api
