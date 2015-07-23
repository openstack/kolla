#!/bin/bash
set -o errexit

CMD="/usr/bin/neutron-linuxbridge-agent"
ARGS="--config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-dir /etc/neutron"

# Loading common functions.
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-sudoers.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

exec $CMD $ARGS
