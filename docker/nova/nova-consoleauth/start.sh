#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

exec $CMD
