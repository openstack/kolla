#!/bin/bash

set -o errexit

# Loading common functions
source /opt/kolla/kolla-common.sh

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    CMD="/usr/sbin/apache2"
    ARGS="-DFOREGROUND"

    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
else
    CMD="/usr/sbin/httpd"
    ARGS="-DFOREGROUND"
fi

# Execute config strategy
set_configs

exec $CMD $ARGS
