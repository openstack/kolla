#!/bin/bash
SOURCE="/opt/kolla/keepalived/keepalived.conf"
TARGET="/etc/keepalived/keepalived.conf"
OWNER="root"

if [[ -f "$SOURCE" ]]; then
    rm $TARGET
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
