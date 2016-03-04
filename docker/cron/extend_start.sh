#!/bin/bash

# NOTE(elemoine): the cron daemon sends its logs to /dev/log. Heka's log socket
# is at /var/lib/kolla/heka/log so we symlink /dev/log to that location.
if [[ ! -h /dev/log ]]; then
    ln -sf /var/lib/kolla/heka/log /dev/log
fi
