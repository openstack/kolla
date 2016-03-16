#!/bin/bash

# We are intentionally not using exec so we can reload the haproxy config later
echo "Running command: '${CMD}'"
$CMD

# TODO(SamYaple): This has the potential for a race condition triggered by a
#                 config reload that could cause the container to exit
while [[ -e "/proc/$(cat /run/haproxy.pid)" ]]; do
    sleep 5
done

# Based on the above loop this point should never be reached
exit 1
