#!/bin/bash

bridge=$1
port=$2

ip link show $port
if [[ $? -ne 0 ]]; then
    # fail when device doesn't exist
    exit 1
fi

ovs-vsctl br-exists $bridge
if [[ $? -eq 2 ]]; then
    changed=changed
    ovs-vsctl --no-wait add-br $bridge
fi

if [[ ! $(ovs-vsctl list-ports $bridge) =~ $(echo "\<$port\>") ]]; then
    changed=changed
    ovs-vsctl --no-wait add-port $bridge $port
fi

echo $changed
