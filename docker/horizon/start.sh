#!/bin/bash
set -o errexit

# Loading common functions
source /opt/kolla/kolla-common.sh

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
fi

exec $CMD
