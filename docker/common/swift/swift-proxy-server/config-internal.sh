#!/bin/bash

set -e

CMD="/usr/bin/swift-proxy-server"
ARGS="/etc/swift/proxy-server.conf --verbose"

. /opt/kolla/config-swift.sh

check_required_vars \
    SWIFT_ACCOUNT_SVC_RING_DEVICES \
    SWIFT_ACCOUNT_SVC_RING_HOSTS \
    SWIFT_ACCOUNT_SVC_RING_MIN_PART_HOURS \
    SWIFT_ACCOUNT_SVC_RING_NAME \
    SWIFT_ACCOUNT_SVC_RING_PART_POWER \
    SWIFT_ACCOUNT_SVC_RING_REPLICAS \
    SWIFT_ACCOUNT_SVC_RING_WEIGHTS \
    SWIFT_ACCOUNT_SVC_RING_ZONES \
    SWIFT_ADMIN_USER \
    SWIFT_CONTAINER_SVC_RING_DEVICES \
    SWIFT_CONTAINER_SVC_RING_HOSTS \
    SWIFT_CONTAINER_SVC_RING_MIN_PART_HOURS \
    SWIFT_CONTAINER_SVC_RING_NAME \
    SWIFT_CONTAINER_SVC_RING_PART_POWER \
    SWIFT_CONTAINER_SVC_RING_REPLICAS \
    SWIFT_CONTAINER_SVC_RING_WEIGHTS \
    SWIFT_CONTAINER_SVC_RING_ZONES \
    SWIFT_KEYSTONE_PASSWORD \
    SWIFT_KEYSTONE_USER \
    SWIFT_OBJECT_SVC_RING_DEVICES \
    SWIFT_OBJECT_SVC_RING_HOSTS \
    SWIFT_OBJECT_SVC_RING_MIN_PART_HOURS \
    SWIFT_OBJECT_SVC_RING_NAME \
    SWIFT_OBJECT_SVC_RING_PART_POWER \
    SWIFT_OBJECT_SVC_RING_REPLICAS \
    SWIFT_OBJECT_SVC_RING_WEIGHTS \
    SWIFT_OBJECT_SVC_RING_ZONES \
    SWIFT_PROXY_ACCOUNT_AUTOCREATE \
    SWIFT_PROXY_AUTH_PLUGIN \
    SWIFT_PROXY_BIND_IP \
    SWIFT_PROXY_BIND_PORT \
    SWIFT_PROXY_DELAY_AUTH_DECISION \
    SWIFT_PROXY_DIR \
    SWIFT_PROXY_OPERATOR_ROLES \
    SWIFT_PROXY_PASSWORD \
    SWIFT_PROXY_PIPELINE_MAIN \
    SWIFT_PROXY_PROJECT_DOMAIN_ID \
    SWIFT_PROXY_PROJECT_NAME \
    SWIFT_PROXY_SIGNING_DIR \
    SWIFT_PROXY_USER_DOMAIN_ID \
    SWIFT_PROXY_USERNAME \
    SWIFT_USER

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"

crux user-create --update \
    -n "${SWIFT_KEYSTONE_USER}" \
    -p "${SWIFT_KEYSTONE_PASSWORD}" \
    -t "${ADMIN_TENANT_NAME}" \
    -r admin

crux endpoint-create --remove-all \
    -n swift -t object-store \
    -I "http://${SWIFT_API_SERVICE_HOST}:8080/v1/AUTH_%(tenant_id)s'" \
    -P "http://${PUBLIC_IP}:8080/v1/AUTH_%(tenant_id)s" \
    -A "http://${SWIFT_API_SERVICE_HOST}:8080'"

cfg=/etc/swift/proxy-server.conf

crudini --set $cfg DEFAULT bind_port "${SWIFT_PROXY_BIND_PORT}"
crudini --set $cfg DEFAULT user "${SWIFT_USER}"
crudini --set $cfg DEFAULT swift_dir "${SWIFT_PROXY_DIR}"
crudini --set $cfg DEFAULT bind_ip "${SWIFT_PROXY_BIND_IP}"

crudini --set $cfg pipeline:main pipeline "${SWIFT_PROXY_PIPELINE_MAIN}"

crudini --set $cfg app:proxy-server account_autocreate "${SWIFT_PROXY_ACCOUNT_AUTOCREATE}"

crudini --del $cfg filter:keystone
crudini --set $cfg filter:keystoneauth use egg:swift#keystoneauth
crudini --set $cfg filter:keystoneauth operator_roles "${SWIFT_PROXY_OPERATOR_ROLES}"

crudini --set $cfg filter:container_sync use egg:swift#container_sync

crudini --set $cfg filter:bulk use egg:swift#bulk

crudini --set $cfg filter:ratelimit use egg:swift#ratelimit

crudini --set $cfg filter:authtoken auth_uri \
    "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/"
crudini --set $cfg filter:authtoken auth_url \
    "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/"
crudini --set $cfg filter:authtoken auth_host "${KEYSTONE_PUBLIC_SERVICE_HOST}"
crudini --set $cfg filter:authtoken auth_port "${KEYSTONE_ADMIN_SERVICE_PORT}"
crudini --set $cfg filter:authtoken admin_tenant_name "${ADMIN_TENANT_NAME}"
crudini --set $cfg filter:authtoken admin_user "${SWIFT_KEYSTONE_USER}"
crudini --set $cfg filter:authtoken admin_password "${SWIFT_KEYSTONE_PASSWORD}"
crudini --set $cfg filter:authtoken delay_auth_decision "${SWIFT_PROXY_DELAY_AUTH_DECISION}"
crudini --set $cfg filter:authtoken signing_dir "${SWIFT_PROXY_SIGNING_DIR}"

crudini --set $cfg filter:cache memcache_servers "${PUBLIC_IP}:11211"

crudini --set $cfg filter:gatekeeper use egg:swift#gatekeeper

crudini --set $cfg filter:slo use egg:swift#slo

crudini --set $cfg filter:dlo use egg:swift#dlo

# Create swift user and group if they don't exist
id -u swift &>/dev/null || useradd --user-group swift

# TODO(pbourke): should these go into the Dockerfile instead?
# TODO(pbourke): do we need a data vol for these?
mkdir -p ${SWIFT_PROXY_SIGNING_DIR}
chown swift: ${SWIFT_PROXY_SIGNING_DIR}
chmod 0700 ${SWIFT_PROXY_SIGNING_DIR}

python /opt/kolla/build-swift-ring.py \
    -f ${SWIFT_OBJECT_SVC_RING_NAME} \
    -p ${SWIFT_OBJECT_SVC_RING_PART_POWER} \
    -r ${SWIFT_OBJECT_SVC_RING_REPLICAS} \
    -m ${SWIFT_OBJECT_SVC_RING_MIN_PART_HOURS} \
    -H ${SWIFT_OBJECT_SVC_RING_HOSTS} \
    -w ${SWIFT_OBJECT_SVC_RING_WEIGHTS} \
    -d ${SWIFT_OBJECT_SVC_RING_DEVICES} \
    -z ${SWIFT_OBJECT_SVC_RING_ZONES}

python /opt/kolla/build-swift-ring.py \
    -f ${SWIFT_ACCOUNT_SVC_RING_NAME} \
    -p ${SWIFT_ACCOUNT_SVC_RING_PART_POWER} \
    -r ${SWIFT_ACCOUNT_SVC_RING_REPLICAS} \
    -m ${SWIFT_ACCOUNT_SVC_RING_MIN_PART_HOURS} \
    -H ${SWIFT_ACCOUNT_SVC_RING_HOSTS} \
    -w ${SWIFT_ACCOUNT_SVC_RING_WEIGHTS} \
    -d ${SWIFT_ACCOUNT_SVC_RING_DEVICES} \
    -z ${SWIFT_ACCOUNT_SVC_RING_ZONES}

python /opt/kolla/build-swift-ring.py \
    -f ${SWIFT_CONTAINER_SVC_RING_NAME} \
    -p ${SWIFT_CONTAINER_SVC_RING_PART_POWER} \
    -r ${SWIFT_CONTAINER_SVC_RING_REPLICAS} \
    -m ${SWIFT_CONTAINER_SVC_RING_MIN_PART_HOURS} \
    -H ${SWIFT_CONTAINER_SVC_RING_HOSTS} \
    -w ${SWIFT_CONTAINER_SVC_RING_WEIGHTS} \
    -d ${SWIFT_CONTAINER_SVC_RING_DEVICES} \
    -z ${SWIFT_CONTAINER_SVC_RING_ZONES}

exec $CMD $ARGS
