#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

modprobe openvswitch

exec $CMD
