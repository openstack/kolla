#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

echo "Running command: ${CMD}"
exec $CMD
