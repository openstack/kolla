#!/bin/bash
SOURCE="/opt/kolla/memcached/memcached.conf"
TARGET="/etc/memcached.conf"
OWNER="memcached"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
