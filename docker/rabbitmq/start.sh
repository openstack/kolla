#!/bin/bash

set -o errexit

# loading common functions
source /opt/kolla/kolla-common.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

# loading functions
source /opt/kolla/config-rabbit.sh

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    set_rabbitmq_cookie
    exit 0
fi

echo "Running command: ${CMD}"
exec $CMD
