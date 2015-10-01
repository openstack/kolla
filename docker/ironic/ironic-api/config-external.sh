#!/bin/bash

SOURCE="/var/lib/kolla/ironic-api/ironic.conf"
TARGET="/etc/ironic/ironic.conf"
OWNER="ironic"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
