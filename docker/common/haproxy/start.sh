#!/bin/bash
set -o errexit

CMD='/usr/sbin/haproxy'
ARGS="-f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

# We are intentionally not using exec so we can reload the haproxy config later
$CMD $ARGS

# TODO(SamYaple): This has the potential for a race condition triggered by a
#                 config reload that could cause the container to exit
while [[ -e "/proc/$(cat /run/haproxy.pid)" ]]; do
    sleep 5
done
