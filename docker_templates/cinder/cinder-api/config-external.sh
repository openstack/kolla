#!/bin/bash
SOURCE="/opt/kolla/cinder-api/cinder.conf"
TARGET="/etc/cinder/cinder.conf"
OWNER="cinder"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
