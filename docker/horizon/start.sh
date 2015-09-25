#!/bin/bash

set -o errexit

# Loading common functions
source /opt/kolla/kolla-common.sh

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
fi

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

exec $CMD
