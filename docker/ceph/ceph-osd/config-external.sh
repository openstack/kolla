#!/bin/bash
SOURCE="/opt/kolla/ceph-osd/ceph.conf"
TARGET="/etc/ceph/ceph.conf"
OWNER="ceph"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi

SOURCE="/opt/kolla/ceph-osd/ceph.client.admin.keyring"
TARGET="/etc/ceph/ceph.client.admin.keyring"
OWNER="ceph"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0600 $TARGET
fi
