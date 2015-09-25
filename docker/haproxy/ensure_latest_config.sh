#!/bin/bash

CURRENT_CONFIG_HASH=$(sha1sum /etc/haproxy/haproxy.cfg | cut -f1 -d' ')
NEW_CONFIG_HASH=$(sha1sum /opt/kolla/config_files/haproxy.cfg | cut -f1 -d' ')

if [[ $CURRENT_CONFIG_HASH != $NEW_CONFIG_HASH ]]; then
    changed=changed
    source /opt/kolla/config-external.sh
    /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -sf $(cat /run/haproxy.pid)
fi

echo $changed
