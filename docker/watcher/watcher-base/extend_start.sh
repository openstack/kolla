#!/bin/bash

if [[ ! -d "/var/log/kolla/watcher" ]]; then
    mkdir -p /var/log/kolla/watcher
fi
if [[ $(stat -c %a /var/log/kolla/watcher) != "755" ]]; then
    chmod 755 /var/log/kolla/watcher
fi

. /usr/local/bin/kolla_watcher_extend_start
