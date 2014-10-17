#!/bin/sh

set -e

. /opt/kolla/config-nova-compute.sh

# ideally this would be a separate container, but because of libguestfs RFEs
# this is not possible.
. /opt/kolla/libvirt-start.sh

sleep 5

exec /usr/bin/nova-compute
