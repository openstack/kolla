#!/bin/bash

if [[ -f "/dev/log" ]]; then
    rm "/dev/log"
fi

SOURCE="/opt/kolla/rsyslog/rsyslog.conf"
TARGET="/etc/rsyslog.conf"
OWNER="root"

if [[ -f "$SOURCE" ]]; then
    rm $TARGET
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
