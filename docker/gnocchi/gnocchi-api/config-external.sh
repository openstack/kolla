#!/bin/bash
SOURCE="/opt/kolla/gnocchi-api/gnocchi-api.conf"
TARGET="/etc/gnocchi/gnocchi-api.conf"
OWNER="gnocchi"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
