#!/bin/bash
SOURCE="/opt/kolla/barbican/barbican.conf"
TARGET="/etc/barbican/barbican.conf"
OWNER="barbican"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
