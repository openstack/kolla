#!/bin/bash

if [[ ! -d "/var/log/kolla/redis" ]]; then
    mkdir -p /var/log/kolla/redis
fi

if [[ $(stat -c %a /var/log/kolla/redis) != "755" ]]; then
    chmod 755 /var/log/kolla/redis
fi

# The CONFIG REWRITE command rewrites the redis.conf
# file the server was started with, applying the minimal
# changes needed to make it reflect the configuration
# currently used by the server, which may be different
# compared to the original one because of the use of
# the CONFIG SET command.
#
# https://redis.io/commands/config-rewrite/
#
# Because of above behaviour it's needed to
# hack kolla's CMD.
#
# Without this hack
# /usr/local/bin/kolla_set_configs --check
# is always reporting changed.
#
# Therefore redis-sentinel is always restarted
# even if configuration is not changed from
# kolla-ansible side.
if [ ! -z "${REDIS_CONF}" ] && [ ! -z ${REDIS_GEN_CONF} ]; then
    cp ${REDIS_CONF} ${REDIS_GEN_CONF}
fi
