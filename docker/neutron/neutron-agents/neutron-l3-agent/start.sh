#!/bin/bash
set -o errexit

# Loading common functions.
source /var/lib/kolla/config-sudoers.sh

# Will be removed when this container is broken out into thin containers
CMD="neutron-l3-agent"
ARGS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/l3_agent.ini --config-file /etc/neutron/fwaas_driver.ini --config-file /etc/neutron/plugins/ml2/ml2_conf.ini"

exec $CMD $ARGS
