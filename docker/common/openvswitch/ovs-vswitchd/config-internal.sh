#!/bin/bash

set -o errexit

check_required_vars OVS_UNIXSOCK

modprobe openvswitch

mkdir -p "$(dirname $OVS_UNIXSOCK)"

exec ovs-vswitchd unix:"${OVS_UNIXSOCK}" -vconsole:emer -vsyslog:err -vfile:info --mlockall --log-file="${OVS_LOG_FILE}"

