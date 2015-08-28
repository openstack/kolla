#!/bin/bash
SOURCE="/opt/kolla/zaqar/zaqar.conf"
TARGET="/etc/zaqar/zaqar.conf"
OWNER="zaqar"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
