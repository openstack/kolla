#!/bin/bash

if [[ -f /opt/kolla/swift/swift.conf ]]; then
    cp /opt/kolla/swift/swift.conf /etc/swift/
    chown swift: /opt/kolla/swift/swift.conf
    chmod 0640 /etc/swift/swift.conf
fi

if [[ -f /opt/kolla/swift/object-server.conf ]]; then
    cp /opt/kolla/swift/object-server.conf /etc/swift/
    chown swift: /opt/kolla/swift/object-server.conf
    chmod 0640 /etc/swift/object-server.conf
fi
