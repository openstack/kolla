#!/bin/bash

# NOTE(elemoine): keepalived cannot be configured to change the log address to
# anything other than /dev/log. Heka's log socket is at /var/lib/kolla/heka/log
# so we symlink /dev/log to that location.
if [[ ! -h /dev/log ]]; then
    ln -sf /var/lib/kolla/heka/log /dev/log
fi

modprobe ip_vs

# Workaround for bug #1485079
if [ -f /run/keepalived.pid ]; then
    rm /run/keepalived.pid
fi
