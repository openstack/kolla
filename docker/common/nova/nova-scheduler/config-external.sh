#!/bin/bash
SOURCE="/opt/kolla/nova-scheduler/nova.conf"
TARGET="/etc/nova/nova.conf"
OWNER="nova"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
