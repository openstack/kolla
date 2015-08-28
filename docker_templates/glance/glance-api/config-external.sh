#!/bin/bash
SOURCE="/opt/kolla/glance-api/glance-api.conf"
TARGET="/etc/glance/glance-api.conf"
OWNER="glance"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
