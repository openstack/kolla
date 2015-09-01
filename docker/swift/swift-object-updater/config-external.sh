#!/bin/bash

OWNER="swift"

if [[ -f "/opt/kolla/swift/swift.conf" ]]; then
    cp /opt/kolla/swift/swift.conf /etc/swift/swift.conf
    chown ${OWNER}: /etc/swift/swift.conf
    chmod 0640 /etc/swift/swift.conf
fi

if [[ -f "/opt/kolla/swift/object.ring.gz" ]]; then
    cp /opt/kolla/swift/object.ring.gz /etc/swift/object.ring.gz
    chown ${OWNER}: /etc/swift/object.ring.gz
    chmod 0640 /etc/swift/object.ring.gz
fi

if [[ -f "/opt/kolla/swift/container.ring.gz" ]]; then
    cp /opt/kolla/swift/container.ring.gz /etc/swift/container.ring.gz
    chown ${OWNER}: /etc/swift/container.ring.gz
    chmod 0640 /etc/swift/container.ring.gz
fi

if [[ -f "/opt/kolla/swift-object-updater/object-updater.conf" ]]; then
    cp /opt/kolla/swift-object-updater/object-updater.conf /etc/swift/object-updater.conf
    chown ${OWNER}: /etc/swift/object-updater.conf
    chmod 0640 /etc/swift/object-updater.conf
fi
