#!/bin/bash

set -o errexit

LOG_FILE="/var/log/openvswitch/ovsdb-server.log"
DB_FILE="/etc/openvswitch/conf.db"
UNIXSOCK_DIR="/var/run/openvswitch"
UNIXSOCK="${UNIXSOCK_DIR}/db.sock"

CMD="/usr/sbin/ovsdb-server"
ARGS="$DB_FILE -vconsole:emer -vsyslog:err -vfile:info --remote=punix:${UNIXSOCK} --log-file=${LOG_FILE}"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

mkdir -p "${UNIXSOCK_DIR}"

if [[ ! -e "${DB_FILE}" ]]; then
    ovsdb-tool create "${DB_FILE}"
fi

exec $CMD $ARGS
