#!/bin/bash

# Only update permissions if permissions need to be updated
if [[ $(stat -c %U:%G /var/lib/zookeeper) != "zookeeper:zookeeper" ]]; then
    sudo chown zookeeper: /var/lib/zookeeper
fi
