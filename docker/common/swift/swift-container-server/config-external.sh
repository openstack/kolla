#!/bin/bash
SOURCE="/opt/kolla/swift/swift.conf"
TARGET="/etc/swift/swift.conf"
SOURCE_CONTAINER_SERVER="/opt/kolla/swift/container-server.conf"
TARGET_CONTAINER_SERVER="/etc/swift/container-server.conf"
OWNER="swift"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0640 $TARGET
fi

if [[ -f "$SOURCE_CONTAINER_SERVER" ]]; then
    cp $SOURCE_CONTAINER_SERVER $TARGET_CONTAINER_SERVER
    chown ${OWNER}: $TARGET_CONTAINER_SERVER
    chmod 0640 $TARGET_CONTAINER_SERVER
fi
