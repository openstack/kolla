#!/bin/bash

# Gracefully stop swift proxy and exit if KOLLA_STOP_SERVICES variable is set.
if [[ "${!KOLLA_STOP_SERVICES[@]}" ]]; then
    echo "Gracefully Shutdown all Swift proxy processes"
    swift-init proxy shutdown
    exit
fi
