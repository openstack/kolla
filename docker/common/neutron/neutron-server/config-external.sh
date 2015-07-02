#!/bin/bash
SOURCE="/opt/kolla/neutron-server/neutron.conf"
TARGET="/etc/neutron/neutron.conf"
OWNER="neutron"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
