#!/bin/bash
# Usage: $0 BRIDGE PEER_BRIDGE
# Creates patch connection between BRIDGE and PEER_BRIDGE. Each bridge has a
# patch port created that is peered with a corresponding port on the
# other bridge.

if [[ $# -lt 2 ]]; then
  exit 1
fi

declare -A peers=( [$1]=$2 [$2]=$1 )

# Ensure all bridges created first; otherwise adding peer ports might fail.
for bridge in "${!peers[@]}"; do
  ovs-vsctl br-exists $bridge
  if [[ $? -eq 2 ]]; then
      changed=changed
      ovs-vsctl --no-wait add-br $bridge
  fi
done

# (diurnalist): Batch all commands at once. This is needed because we may need
# to create both patch ports, which depend on eachother. Adding them in one
# batch avoids errors in OVS when adding the first port (b/c the second hasn't
# been created yet.)
declare -a batch=()

for bridge in "${!peers[@]}"; do
  peer="${peers[$bridge]}"
  # Remove br- prefixes
  port="${bridge##br-}-${peer##br-}"
  peer_port="${peer##br-}-${bridge##br-}"

  if [[ ! $(ovs-vsctl list-ports $bridge) =~ $(echo "\<$port\>") ]]; then
      changed=changed
      batch+=(-- add-port $bridge $port)
      batch+=(-- set interface $port type=patch options:peer=$peer_port)
  fi
done

ovs-vsctl --no-wait "${batch[@]}"

echo $changed
