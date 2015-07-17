#!/bin/bash
set -o errexit

CMD='/usr/sbin/haproxy'
# Parameters:
# -db for non-daemon execution and logging to stdout
# -p pidfile to specify pidfile and allow hot reconfiguration
# loop which generates -f file.conf for each file in /etc/haproxy and /etc/haproxy/conf.d
ARGS="-db -f /etc/haproxy/haproxy.cfg"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

exec $CMD $ARGS
