#!/bin/sh

# This script should be sourced by kolla_extend_start when bootstrapping
#
# Optional env(<default>):
#   TOPOLOGY_NAME("monasca-thresh") - topology name to check
#   TOPOLOGY_KILL_TIMEOUT(5) - secs to wait for topology kill
#   STORM_WAIT_RETRIES(24) - retries to check for storm
#   STORM_WAIT_TIMEOUT(20) - secs to wait for storm list
#   STORM_WAIT_DELAY(5) - secs between storm list attempts

#  - If topology exists, then:
#     a) if TOPOLOGY_REPLACE is set, the existing topology is killed
#        and script falls through (topology may be added)
#     b) otherwise script exits with 0 (topology already exists)
#  - If topology doesn't exist, script falls through (topology may be added)
#  - If storm cannot be reached, or kill fails, script exits with 1

TOPOLOGY_NAME=${TOPOLOGY_NAME:-monasca-thresh}
TOPOLOGY_KILL_TIMEOUT=${TOPOLOGY_KILL_TIMEOUT:-5}

# defaults from monasca-thresh
STORM_WAIT_RETRIES=${STORM_WAIT_RETRIES:-24}
STORM_WAIT_TIMEOUT=${STORM_WAIT_TIMEOUT:-20}
STORM_WAIT_DELAY=${STORM_WAIT_DELAY:-5}

STORM="/opt/storm/bin/storm"

echo "Waiting for storm to become available..."
success="false"
for i in $(seq "$STORM_WAIT_RETRIES"); do
    if timeout "$STORM_WAIT_TIMEOUT" "$STORM" list; then
        echo "Storm is available, continuing..."
        success="true"
        break
    else
        echo "Connection attempt $i of $STORM_WAIT_RETRIES failed"
        sleep "$STORM_WAIT_DELAY"
    fi
done

if [ "$success" != "true" ]; then
    echo "Unable to connect to Storm! Exiting..."
    sleep 1
    exit 1
fi

locate_topology() { # <topology>
    echo "Searching for topology $1 in the storm"
    topologies=$("$STORM" list | awk '/-----/,0{if (!/-----/)print $1}')
    found="false"
    for topology in $topologies; do
        if [ "$topology" = "$1" ]; then
            echo "Found storm topology with name: $topology"
            found="true"
            break
        fi
    done
}

# search for existing topology
locate_topology "$TOPOLOGY_NAME"

if [ "$found" = "true" ]; then

    if [[ ! "${!TOPOLOGY_REPLACE[@]}" ]]; then
        echo "Topology $TOPOLOGY_NAME found, submission not necessary"
        exit 0
    fi

    echo "Topology replacement requested, killing old one..."
    "$STORM" kill "$TOPOLOGY_NAME" -w "$TOPOLOGY_KILL_TIMEOUT"

    echo "Wait $TOPOLOGY_KILL_TIMEOUT secs for topology to reap its artifacts..."
    sleep "$TOPOLOGY_KILL_TIMEOUT"

    for i in $(seq "$STORM_WAIT_RETRIES"); do
        locate_topology "$TOPOLOGY_NAME"
        [ "$found" != "true" ] && break
        echo "... wait some more..."
        sleep "$STORM_WAIT_DELAY"
    done
    if [ "$found" = "true" ]; then
        echo "Unable to kill existing topology, giving up..."
        exit 1
    fi
    echo "Topology successfully killed, continuing..."
else
    echo "Topology not found, continuing..."
fi
