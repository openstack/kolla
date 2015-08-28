#!/bin/bash
LOG_FILE="/var/log/openvswitch/ovs-vswitchd.log"
DB_FILE="/etc/openvswitch/conf.db"
UNIXSOCK_DIR="/var/run/openvswitch"
UNIXSOCK="${UNIXSOCK_DIR}/db.sock"

CMD="/usr/sbin/ovs-vswitchd"
ARGS="unix:${UNIXSOCK} -vconsole:emer -vsyslog:err -vfile:info --mlockall --log-file=${LOG_FILE}"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

modprobe openvswitch
mkdir -p "${UNIXSOCK_DIR}"

exec $CMD $ARGS
