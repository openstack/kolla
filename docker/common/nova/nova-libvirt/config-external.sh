#!/bin/bash
SOURCE="/opt/kolla/libvirt/libvirt.conf"
TARGET="/etc/libvirt/libvirt.conf"
OWNER="libvirt"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
