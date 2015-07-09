#!/bin/bash

set -e

DESC="target framework daemon"
DAEMON=/usr/sbin/tgtd

TGTD_CONFIG=/etc/tgt/targets.conf

echo "Starting tgtd $DESC"
/usr/sbin/tgtd
echo "Set to offline"
tgtadm --op update --mode sys --name State -v offline
echo "Set tgt config"
tgt-admin -e -c $TGTD_CONFIG
echo "Set to ready"
tgtadm --op update --mode sys --name State -v ready
