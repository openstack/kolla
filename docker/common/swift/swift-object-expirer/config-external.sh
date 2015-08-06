#!/bin/bash
SOURCE="/opt/kolla/swift/swift.conf"
TARGET="/etc/swift/swift.conf"
SOURCE_OBJECT_EXPIRER="/opt/kolla/swift/object-expirer.conf"
TARGET_OBJECT_EXPIRER="/etc/swift/object-expirer.conf"
OWNER="swift"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0640 $TARGET
fi

if [[ -f "$SOURCE_OBJECT_EXPIRER" ]]; then
    cp $SOURCE_OBJECT_EXPIRER $TARGET_OBJECT_EXPIRER
    chown ${OWNER}: $TARGET_OBJECT_EXPIRER
    chmod 0640 $TARGET_OBJECT_EXPIRER
fi
