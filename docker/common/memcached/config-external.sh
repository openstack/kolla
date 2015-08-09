#!/bin/bash
SOURCE="/opt/kolla/memcached/memcached"
TARGET="/etc/sysconfig/memcached"
OWNER="swift"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
