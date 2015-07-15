#!/bin/bash

set -e

CMD="/usr/bin/swift-account-server"
ARGS="/etc/swift/account-server.conf --verbose"

. /opt/kolla/config-swift.sh

check_required_vars \
    SWIFT_ACCOUNT_SVC_BIND_IP \
    SWIFT_ACCOUNT_SVC_BIND_PORT \
    SWIFT_ACCOUNT_SVC_DEVICES \
    SWIFT_ACCOUNT_SVC_MOUNT_CHECK \
    SWIFT_ACCOUNT_SVC_RING_DEVICES \
    SWIFT_ACCOUNT_SVC_RING_HOSTS \
    SWIFT_ACCOUNT_SVC_RING_MIN_PART_HOURS \
    SWIFT_ACCOUNT_SVC_RING_NAME \
    SWIFT_ACCOUNT_SVC_RING_PART_POWER \
    SWIFT_ACCOUNT_SVC_RING_REPLICAS \
    SWIFT_ACCOUNT_SVC_RING_WEIGHTS \
    SWIFT_ACCOUNT_SVC_RING_ZONES \
    SWIFT_DIR \
    SWIFT_USER

exec $CMD $ARGS

cfg=/etc/swift/account-server.conf

# [DEFAULT]
crudini --set $cfg DEFAULT bind_ip "${SWIFT_ACCOUNT_SVC_BIND_IP}"
crudini --set $cfg DEFAULT bind_port "${SWIFT_ACCOUNT_SVC_BIND_PORT}"
crudini --set $cfg DEFAULT user "${SWIFT_USER}"
crudini --set $cfg DEFAULT swift_dir "${SWIFT_DIR}"
crudini --set $cfg DEFAULT devices "${SWIFT_ACCOUNT_SVC_DEVICES}"
crudini --set $cfg DEFAULT mount_check "${SWIFT_ACCOUNT_SVC_MOUNT_CHECK}"

# Create swift user and group if they don't exist
id -u swift &>/dev/null || useradd --user-group swift

# Ensure proper ownership of the mount point directory structure
chown -R swift:swift /srv/node

python /opt/kolla/build-swift-ring.py \
    -f ${SWIFT_ACCOUNT_SVC_RING_NAME} \
    -p ${SWIFT_ACCOUNT_SVC_RING_PART_POWER} \
    -r ${SWIFT_ACCOUNT_SVC_RING_REPLICAS} \
    -m ${SWIFT_ACCOUNT_SVC_RING_MIN_PART_HOURS} \
    -H ${SWIFT_ACCOUNT_SVC_RING_HOSTS} \
    -w ${SWIFT_ACCOUNT_SVC_RING_WEIGHTS} \
    -d ${SWIFT_ACCOUNT_SVC_RING_DEVICES} \
    -z ${SWIFT_ACCOUNT_SVC_RING_ZONES}

exec $CMD $ARGS
