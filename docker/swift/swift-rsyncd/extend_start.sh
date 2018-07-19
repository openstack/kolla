#!/bin/bash

sudo chown -R swift:swift /srv/node
mkdir -p /var/lib/swift/lock

# Migrate swift database and exit if KOLLA_STOP_SERVICES variable is set.
if [[ "${!KOLLA_STOP_SERVICES[@]}" ]]; then
    echo "Stop background Swift jobs"
    swift-init rest stop
    echo "Gracefully Shutdown all Swift storage processes"
    swift-init {account|container|object} shutdown
    exit
fi
