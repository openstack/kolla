#!/bin/bash
SOURCE="/opt/kolla/swift/swift.conf"
TARGET="/etc/swift/swift.conf"
SOURCE_OBJECT_SERVER="/opt/kolla/swift/object-server.conf"
TARGET_OBJECT_SERVER="/etc/swift/object-server.conf"
OWNER="swift"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0640 $TARGET
fi

if [[ -f "$SOURCE_OBJECT_SERVER" ]]; then
    cp $SOURCE_OBJECT_SERVER $TARGET_OBJECT_SERVER
    chown ${OWNER}: $TARGET_OBJECT_SERVER
    chmod 0640 $TARGET_OBJECT_SERVER
fi
