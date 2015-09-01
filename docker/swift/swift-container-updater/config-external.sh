#!/bin/bash

OWNER="swift"

if [[ -f "/opt/kolla/swift/swift.conf" ]]; then
    cp /opt/kolla/swift/swift.conf /etc/swift/swift.conf
    chown ${OWNER}: /etc/swift/swift.conf
    chmod 0640 /etc/swift/swift.conf
fi

if [[ -f "/opt/kolla/swift/account.ring.gz" ]]; then
    cp /opt/kolla/swift/account.ring.gz /etc/swift/account.ring.gz
    chown swift: /etc/swift/account.ring.gz
    chmod 0640 /etc/swift/account.ring.gz
fi

if [[ -f "/opt/kolla/swift/container.ring.gz" ]]; then
    cp /opt/kolla/swift/container.ring.gz /etc/swift/container.ring.gz
    chown ${OWNER}: /etc/swift/container.ring.gz
    chmod 0640 /etc/swift/container.ring.gz
fi

if [[ -f "/opt/kolla/swift-container-updater/container-updater.conf" ]]; then
    cp /opt/kolla/swift-container-updater/container-updater.conf /etc/swift/container-updater.conf
    chown ${OWNER}: /etc/swift/container-updater.conf
    chmod 0640 /etc/swift/container-updater.conf
fi
