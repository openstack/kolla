#!/bin/bash

. /opt/kolla/kolla-common.sh

check_required_vars KEEPALIVED_HOST_PRIORITIES \
                    PUBLIC_INTERFACE \
                    PUBLIC_IP

MY_HOSTNAME=`hostname`

# here we unpack KEEPALIVED_HOST_PRIORITIES hostname:priority pairs and match
# them with current hostname, if it's there
for i in ${KEEPALIVED_HOST_PRIORITIES//,/ }; do
    HOST_PRIORITY=(${i//:/ })
    if [ "$MY_HOSTNAME" == "${HOST_PRIORITY[0]}" ]; then
        KEEPALIVED_PRIORITY=${HOST_PRIORITY[1]}
    fi
done

if [ -z "$KEEPALIVED_PRIORITY" ]; then
    echo "ERROR: missing hostname in KEEPALIVED_HOST_PRIORITIES: $MY_HOSTNAME" >&2
    exit 1
fi

sed -i '
    s|@PUBLIC_INTERFACE@|'$PUBLIC_INTERFACE'|g
    s|@PUBLIC_IP@|'$PUBLIC_IP'|g
    s|@KEEPALIVED_PRIORITY@|'$KEEPALIVED_PRIORITY'|g
' /etc/keepalived/keepalived.conf

exec /usr/sbin/keepalived -nld -p /run/keepalived.pid
