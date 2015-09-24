#!/bin/bash
SOURCE="/opt/kolla/memcached/memcached.conf"
TARGET="/etc/memcached.conf"
OWNER="memcached"

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    OWNER="memcache"
else
    OWNER="memcached"
fi

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
