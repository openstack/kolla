#!/bin/bash

set -o errexit

modprobe openvswitch

LOG_FILE="/var/log/openvswitch/ovs-vswitchd.log"
DB_FILE="/etc/openvswitch/conf.db"
UNIXSOCK_DIR="/var/run/openvswitch"
UNIXSOCK="${UNIXSOCK_DIR}/db.sock"

mkdir -p "${UNIXSOCK_DIR}"

exec ovs-vswitchd unix:"${UNIXSOCK}" -vconsole:emer -vsyslog:err -vfile:info --mlockall --log-file="${LOG_FILE}"
