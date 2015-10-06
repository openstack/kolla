#!/bin/bash
set -o errexit

# Loading common functions.
source /var/lib/kolla/config-sudoers.sh

# Will be removed when this container is broken out in thin containers
CMD="/usr/bin/neutron-metadata-agent"
ARGS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/metadata_agent.ini"

exec $CMD $ARGS
