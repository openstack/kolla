#!/bin/bash
set -o errexit

CMD="/usr/bin/neutron-openvswitch-agent"
ARGS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini"

# Loading common functions.
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-sudoers.sh

# Execute config strategy
set_configs

exec $CMD $ARGS
