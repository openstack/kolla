#!/bin/bash

# We are intentionally not using exec so we can reload the haproxy config later
echo "Running command: '${CMD}'"
$CMD

retry=0
# The loop breaks only when haproxy.pid get missing even after 3 re-try.
while [[ $retry -lt 3 ]]; do
    if [[ ! -e /run/haproxy.pid || ! -d /proc/$(cat /run/haproxy.pid) ]]; then
        retry=$((retry+1))
        sleep 2
        continue
    fi
    retry=0
    sleep 5
done

exit 1
