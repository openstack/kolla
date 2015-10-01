#!/bin/bash
SOURCE="/var/lib/kolla/designate/designate.conf"
TARGET="/etc/designate/designate.conf"
OWNER="designate"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
