#!/bin/bash
SOURCE="/opt/kolla/murano/murano.conf"
TARGET="/etc/murano/murano.conf"
OWNER="murano"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
