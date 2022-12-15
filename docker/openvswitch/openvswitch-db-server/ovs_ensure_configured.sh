#!/bin/bash
set -o errexit

bridge=$1
port=$2

if ! ip link show $port; then
    # fail when device doesn't exist
    exit 1
fi

ovs-vsctl br-exists $bridge || if [[ $? -eq 2 ]]; then
    changed=changed
    ovs-vsctl --no-wait add-br $bridge
fi

if [[ ! $(ovs-vsctl list-ports $bridge) =~ $(echo "\<$port\>") ]]; then
    changed=changed
    ovs-vsctl --no-wait add-port $bridge $port
fi

echo $changed
