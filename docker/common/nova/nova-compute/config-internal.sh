#!/bin/bash

set -e

. /opt/kolla/config-nova-compute.sh

sleep 6

# https://bugs.launchpad.net/kolla/+bug/1461635
# Cinder requires mounting /dev in the cinder-volume, nova-compute,
# and libvirt containers.  If /dev/pts/ptmx does not have proper permissions
# on the host, then libvirt will fail to boot an instance.
# This is a bug in Docker where it is not correctly mounting /dev/pts
# Tech Debt tracker: https://bugs.launchpad.net/kolla/+bug/1468962
# **Temporary fix**
chmod 666 /dev/pts/ptmx

echo "Starting nova-compute."
exec /usr/bin/nova-compute --config-file /etc/nova/nova.conf
