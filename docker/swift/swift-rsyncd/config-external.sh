#!/bin/bash

OWNER="swift"

if [[ -f "/opt/kolla/swift-rsyncd/rsyncd.conf" ]]; then
    cp /opt/kolla/swift-rsyncd/rsyncd.conf /etc/rsyncd.conf
    chown ${OWNER}: /etc/rsyncd.conf
    chmod 0640 /etc/rsyncd.conf
fi
