#!/bin/bash
SOURCE="/opt/kolla/glance-registry/glance-registry.conf"
TARGET="/etc/glance/glance-registry.conf"
OWNER="glance"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
