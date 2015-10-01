#!/bin/bash

CURRENT_CONFIG_HASH=$(sha1sum /etc/haproxy/haproxy.cfg | cut -f1 -d' ')
NEW_CONFIG_HASH=$(sha1sum /var/lib/kolla/config_files/haproxy.cfg | cut -f1 -d' ')

if [[ $CURRENT_CONFIG_HASH != $NEW_CONFIG_HASH ]]; then
    changed=changed
    python /usr/local/bin/kolla_set_configs
    /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -sf $(cat /run/haproxy.pid)
fi

echo $changed
