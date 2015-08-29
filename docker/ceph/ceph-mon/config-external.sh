#!/bin/bash
SOURCE="/opt/kolla/ceph-mon/ceph.conf"
TARGET="/etc/ceph/ceph.conf"
OWNER="ceph"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi

SOURCE="/opt/kolla/ceph-mon/ceph.client.admin.keyring"
TARGET="/etc/ceph/ceph.client.admin.keyring"
OWNER="ceph"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0600 $TARGET
fi

SOURCE="/opt/kolla/ceph-mon/ceph.client.mon.keyring"
TARGET="/etc/ceph/ceph.client.mon.keyring"
OWNER="ceph"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0600 $TARGET
fi

SOURCE="/opt/kolla/ceph-mon/ceph.monmap"
TARGET="/etc/ceph/ceph.monmap"
OWNER="ceph"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0600 $TARGET
fi
