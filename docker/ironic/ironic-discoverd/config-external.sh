#!/bin/bash

SOURCE="/opt/kolla/ironic-discoverd/discoverd.conf"
TARGET="/etc/ironic-discoverd/discoverd.conf"
OWNER="ironic"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
