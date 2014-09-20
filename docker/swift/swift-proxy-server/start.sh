#!/bin/sh

sh /opt/swift/config-swift.sh proxy

exec /usr/bin/swift-proxy-server
