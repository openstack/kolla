#!/bin/bash

OWNER="swift"

if [[ -f "/opt/kolla/swift/swift.conf" ]]; then
    cp /opt/kolla/swift/swift.conf /etc/swift/swift.conf
    chown ${OWNER}: /etc/swift/swift.conf
    chmod 0640 /etc/swift/swift.conf
fi

if [[ -f "/opt/kolla/swift/container.ring.gz" ]]; then
    cp /opt/kolla/swift/container.ring.gz /etc/swift/container.ring.gz
    chown ${OWNER}: /etc/swift/container.ring.gz
    chmod 0640 /etc/swift/container.ring.gz
fi

if [[ -f "/opt/kolla/swift-container-server/container-server.conf" ]]; then
    cp /opt/kolla/swift-container-server/container-server.conf /etc/swift/container-server.conf
    chown ${OWNER}: /etc/swift/container-server.conf
    chmod 0640 /etc/swift/container-server.conf
fi
