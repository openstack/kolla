#!/bin/bash

set -o errexit

CMD="/usr/sbin/rabbitmq-server"
ARGS=""

# loading common functions
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

# loading functions
source /opt/kolla/config-rabbit.sh

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    set_rabbitmq_cookie
    exit 0
fi

$CMD $ARGS
