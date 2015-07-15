#!/bin/bash

if [[ -f /opt/kolla/swift/swift.conf ]]; then
    cp /opt/kolla/swift/swift.conf /etc/swift/
    chown swift: /opt/kolla/swift/swift.conf
    chmod 0640 /etc/swift/swift.conf
fi

if [[ -f /opt/kolla/swift/object-expirer.conf ]]; then
    cp /opt/kolla/swift/object-expirer.conf /etc/swift/
    chown swift: /opt/kolla/swift/object-expirer.conf
    chmod 0640 /etc/swift/object-expirer.conf
fi
