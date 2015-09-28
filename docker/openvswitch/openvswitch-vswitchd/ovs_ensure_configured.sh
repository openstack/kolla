#!/bin/bash

bridge=$1
port=$2

ovs-vsctl br-exists $bridge; rc=$?
if [[ $rc == 2 ]]; then
    changed=changed
    ovs-vsctl add-br $bridge
fi

if [[ ! $(ovs-vsctl list-ports $bridge) =~ $(echo "\<$port\>") ]]; then
    changed=changed
    ovs-vsctl add-port $bridge $port
fi

echo $changed
