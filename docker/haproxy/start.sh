#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

# We are intentionally not using exec so we can reload the haproxy config later
$CMD

# TODO(SamYaple): This has the potential for a race condition triggered by a
#                 config reload that could cause the container to exit
while [[ -e "/proc/$(cat /run/haproxy.pid)" ]]; do
    sleep 5
done
