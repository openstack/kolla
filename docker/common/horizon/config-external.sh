#!/bin/bash
SOURCE="/etc/openstack-dashboard/local_settings"
TARGET="/etc/openstack-dashboard/local_settings"
OWNER="horizon"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
