#!/bin/bash
SOURCE="/opt/kolla/haproxy/haproxy.cfg"
TARGET="/etc/haproxy/haproxy.cfg"
OWNER="root"

if [[ -f "$SOURCE" ]]; then
    rm $TARGET
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
