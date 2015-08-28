#!/bin/bash

. /opt/kolla/kolla-common.sh

check_required_vars \
    SWIFT_CONTAINER_SVC_RING_DEVICES \
    SWIFT_CONTAINER_SVC_RING_HOSTS \
    SWIFT_CONTAINER_SVC_RING_MIN_PART_HOURS \
    SWIFT_CONTAINER_SVC_RING_NAME \
    SWIFT_CONTAINER_SVC_RING_PART_POWER \
    SWIFT_CONTAINER_SVC_RING_REPLICAS \
    SWIFT_CONTAINER_SVC_RING_WEIGHTS \
    SWIFT_CONTAINER_SVC_RING_ZONES \
    SWIFT_DIR \
    SWIFT_OBJECT_SVC_BIND_IP \
    SWIFT_OBJECT_SVC_BIND_PORT \
    SWIFT_OBJECT_SVC_DEVICES \
    SWIFT_OBJECT_SVC_MOUNT_CHECK \
    SWIFT_OBJECT_SVC_PIPELINE \
    SWIFT_OBJECT_SVC_RING_DEVICES \
    SWIFT_OBJECT_SVC_RING_HOSTS \
    SWIFT_OBJECT_SVC_RING_MIN_PART_HOURS \
    SWIFT_OBJECT_SVC_RING_NAME \
    SWIFT_OBJECT_SVC_RING_PART_POWER \
    SWIFT_OBJECT_SVC_RING_REPLICAS \
    SWIFT_OBJECT_SVC_RING_WEIGHTS \
    SWIFT_OBJECT_SVC_RING_ZONES \
    SWIFT_USER

cfg=/etc/swift/object-server.conf

crudini --set $cfg DEFAULT bind_ip "${SWIFT_OBJECT_SVC_BIND_IP}"
crudini --set $cfg DEFAULT bind_port "${SWIFT_OBJECT_SVC_BIND_PORT}"
crudini --set $cfg DEFAULT user "${SWIFT_USER}"
crudini --set $cfg DEFAULT swift_dir "${SWIFT_DIR}"
crudini --set $cfg DEFAULT devices "${SWIFT_OBJECT_SVC_DEVICES}"
crudini --set $cfg DEFAULT mount_check "${SWIFT_OBJECT_SVC_MOUNT_CHECK}"

crudini --set $cfg pipeline:main pipeline "${SWIFT_OBJECT_SVC_PIPELINE}"

# NOTE(pbourke): some services require a section in the conf, even if empty
crudini --set $cfg object-expirer

# Create swift user and group if they don't exist
id -u swift &>/dev/null || useradd --user-group swift

# Ensure proper ownership of the mount point directory structure
chown -R swift:swift /srv/node

# TODO(pbourke): does this need to be on a data vol?
mkdir -p /var/cache/swift
chown -R swift:swift /var/cache/swift

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
    -f ${SWIFT_CONTAINER_SVC_RING_NAME} \
    -p ${SWIFT_CONTAINER_SVC_RING_PART_POWER} \
    -r ${SWIFT_CONTAINER_SVC_RING_REPLICAS} \
    -m ${SWIFT_CONTAINER_SVC_RING_MIN_PART_HOURS} \
    -H ${SWIFT_CONTAINER_SVC_RING_HOSTS} \
    -w ${SWIFT_CONTAINER_SVC_RING_WEIGHTS} \
    -d ${SWIFT_CONTAINER_SVC_RING_DEVICES} \
    -z ${SWIFT_CONTAINER_SVC_RING_ZONES}
