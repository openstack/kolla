#!/bin/bash
set -o errexit

# loading common functions
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-rabbit.sh

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    set_rabbitmq_cookie
    exit 0
fi

exec $CMD
