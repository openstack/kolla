#!/bin/bash
set -o errexit

CMD="/usr/bin/neutron-openvswitch-agent"
ARGS="--config-file /etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

exec $CMD $ARGS
