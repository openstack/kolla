#!/bin/bash
SOURCE="/opt/kolla/libvirt/libvirtd.conf"
TARGET="/etc/libvirt/libvirtd.conf"
OWNER="libvirt"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
