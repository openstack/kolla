#!/bin/bash

set -e

CMD="/usr/bin/swift-container-server"
ARGS="/etc/swift/container-server.conf --verbose"

. /opt/kolla/config-swift.sh

check_required_vars \
    SWIFT_CONTAINER_SVC_BIND_IP \
    SWIFT_CONTAINER_SVC_BIND_PORT \
    SWIFT_CONTAINER_SVC_DEVICES \
    SWIFT_CONTAINER_SVC_MOUNT_CHECK \
    SWIFT_CONTAINER_SVC_RING_DEVICES \
    SWIFT_CONTAINER_SVC_RING_HOSTS \
    SWIFT_CONTAINER_SVC_RING_MIN_PART_HOURS \
    SWIFT_CONTAINER_SVC_RING_NAME \
    SWIFT_CONTAINER_SVC_RING_PART_POWER \
    SWIFT_CONTAINER_SVC_RING_REPLICAS \
    SWIFT_CONTAINER_SVC_RING_WEIGHTS \
    SWIFT_CONTAINER_SVC_RING_ZONES \
    SWIFT_DIR \
    SWIFT_USER

cfg=/etc/swift/container-server.conf

# [DEFAULT]
crudini --set $cfg DEFAULT bind_ip "${SWIFT_CONTAINER_SVC_BIND_IP}"
crudini --set $cfg DEFAULT bind_port "${SWIFT_CONTAINER_SVC_BIND_PORT}"
crudini --set $cfg DEFAULT user "${SWIFT_USER}"
crudini --set $cfg DEFAULT swift_dir "${SWIFT_DIR}"
crudini --set $cfg DEFAULT devices "${SWIFT_CONTAINER_SVC_DEVICES}"
crudini --set $cfg DEFAULT mount_check "${SWIFT_CONTAINER_SVC_MOUNT_CHECK}"

# Create swift user and group if they don't exist
id -u swift &>/dev/null || useradd --user-group swift

# Ensure proper ownership of the mount point directory structure
chown -R swift:swift /srv/node

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
