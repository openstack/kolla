#!/bin/bash

if [[ -f /opt/kolla/swift/swift.conf ]]; then
    cp /opt/kolla/swift/swift.conf /etc/swift/
    chown swift: /etc/swift/swift.conf
    chmod 0640 /etc/swift/swift.conf
fi

if [[ -f "/opt/kolla/swift/account.ring.gz" ]]; then
    cp /opt/kolla/swift/account.ring.gz /etc/swift/account.ring.gz
    chown swift: /etc/swift/account.ring.gz
    chmod 0640 /etc/swift/account.ring.gz
fi

if [[ -f /opt/kolla/swift-account-server/account-server.conf ]]; then
    cp /opt/kolla/swift-account-server/account-server.conf /etc/swift/
    chown swift: /etc/swift/account-server.conf
    chmod 0640 /etc/swift/account-server.conf
fi
