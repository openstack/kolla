#!/bin/bash

set -e

# Run Kolla common script
echo "Running the kolla-common script"
. /opt/kolla/kolla-common.sh

# TODO: Flags..
: ${VERBOSE_LOGGING:=true}
: ${DEBUG_LOGGING:=false}
: ${USE_STDERR:=false}

# SERVICE SECTION
echo "STARTING OVS..."
/usr/share/openvswitch/scripts/ovs-ctl start --system-id=random
tailf /var/log/openvswitch/ovs-vswitchd.log
