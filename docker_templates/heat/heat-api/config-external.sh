#!/bin/bash
SOURCE="/opt/kolla/heat-api/heat-api.conf"
TARGET="/etc/heat/heat-api.conf"
OWNER="heat"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
