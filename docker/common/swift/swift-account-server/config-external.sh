#!/bin/bash
SOURCE="/opt/kolla/swift/swift.conf"
TARGET="/etc/swift/swift.conf"
SOURCE_ACCOUNT_SERVER="/opt/kolla/swift/account-server.conf"
TARGET_ACCOUNT_SERVER="/etc/swift/account-server.conf"
OWNER="swift"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0640 $TARGET
fi

if [[ -f "$SOURCE_ACCOUNT_SERVER" ]]; then
    cp $SOURCE_ACCOUNT_SERVER $TARGET_ACCOUNT_SERVER
    chown ${OWNER}: $TARGET_ACCOUNT_SERVER
    chmod 0640 $TARGET_ACCOUNT_SERVER
fi
