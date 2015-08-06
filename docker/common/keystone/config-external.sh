#!/bin/bash
SOURCE="/opt/kolla/keystone/keystone.conf"
TARGET="/etc/keystone/keystone.conf"
SOURCE_WSGI="/opt/kolla/keystone/wsgi-keystone.conf"
TARGET_WSGI="/etc/httpd/conf.d/wsgi-keystone.conf"
OWNER="keystone"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi

if [[ -f "$SOURCE_WSGI" ]]; then
    cp $SOURCE_WSGI $TARGET_WSGI
    chown ${OWNER}: $TARGET_WSGI
    chmod 0644 $TARGET_WSGI
fi
