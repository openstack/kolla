#!/bin/bash
SOURCE="/opt/kolla/ceilometer/ceilometer.conf"
TARGET="/etc/ceilometer/ceilometer.conf"
OWNER="ceilometer"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
