#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-sudoers.sh

exec $CMD
