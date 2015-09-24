#!/bin/bash

set -o errexit

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    CMD="/usr/bin/memcached"
    ARGS="-u memcache -vv"
else
    CMD="/usr/bin/memcached"
    ARGS="-u memcached -vv"
fi

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

source /etc/memcached.conf

exec $CMD $ARGS $OPTIONS
