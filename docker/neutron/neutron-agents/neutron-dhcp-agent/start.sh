#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/config-sudoers.sh

# Will be removed when neutron-agents is a thin container
CMD="/usr/bin/neutron-dhcp-agent"
ARGS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/dhcp_agent.ini"

exec $CMD $ARGS
