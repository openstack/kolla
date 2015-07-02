#!/bin/bash
SOURCE="/opt/kolla/heat-engine/heat.conf"
TARGET="/etc/heat/heat.conf"
OWNER="heat"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
