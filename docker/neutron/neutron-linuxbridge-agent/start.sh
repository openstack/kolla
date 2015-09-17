#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-sudoers.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

exec $CMD
