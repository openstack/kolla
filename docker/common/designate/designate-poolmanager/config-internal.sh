#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-designate.sh

check_required_vars DESIGNATE_BACKEND \
                    DESIGNATE_DNS_PORT \
                    DESIGNATE_MASTERNS \
                    DESIGNATE_MDNS_PORT \
                    DESIGNATE_POOLMAN_NSS \
                    DESIGNATE_POOLMAN_POOLID \
                    DESIGNATE_POOLMAN_TARGETS \
                    DESIGNATE_SLAVENS

CONF=/etc/designate/designate.conf

if [ "${DESIGNATE_BACKEND}" == "bind9" ]; then
    TYPE="bind9"
    OPTIONS="rndc_host: ${DESIGNATE_SLAVENS}, rndc_key_file: /etc/rndc.key"
else
    echo Unsupported backend: ${DESIGNATE_BACKEND}
    exit
fi

crudini --set $CONF service:pool_manager workers "1"
crudini --set $CONF service:pool_manager enable_recovery_timer "False"
crudini --set $CONF service:pool_manager periodic_recovery_interval "120"
crudini --set $CONF service:pool_manager enable_sync_timer "True"
crudini --set $CONF service:pool_manager periodic_sync_interval "1800"
crudini --set $CONF service:pool_manager poll_max_retries "10"
crudini --set $CONF service:pool_manager poll_delay "5"
crudini --set $CONF service:pool_manager poll_retry_interval "15"
crudini --set $CONF service:pool_manager pool_id "${DESIGNATE_POOLMAN_POOLID}"
crudini --set $CONF service:pool_manager cache_driver "noop"

# TODO: use this to use memcached
#crudini --set $CONF service:pool_manager cache_driver memcache
#crudini --set $CONF service:pool_manager memcached_servers ${MEMCACHED_HOST}

# Specify the id of the pool managed through pool_manager. Central gets
# configured with this pool_id as well.
crudini --set $CONF service:pool_manager pool_id "${DESIGNATE_POOLMAN_POOLID}"

crudini --set $CONF pool:${DESIGNATE_POOLMAN_POOLID} nameservers "${DESIGNATE_POOLMAN_NSS}"
crudini --set $CONF pool:${DESIGNATE_POOLMAN_POOLID} targets "${DESIGNATE_POOLMAN_TARGETS}"

crudini --set $CONF pool_target:${DESIGNATE_POOLMAN_TARGETS} type "${TYPE}"
crudini --set $CONF pool_target:${DESIGNATE_POOLMAN_TARGETS} options "${OPTIONS}"
# This is the mdns container, which is the master nameserver.
crudini --set $CONF pool_target:${DESIGNATE_POOLMAN_TARGETS} masters "${DESIGNATE_MASTERNS}:${DESIGNATE_MDNS_PORT}"
crudini --set $CONF pool_target:${DESIGNATE_POOLMAN_TARGETS} host "${DESIGNATE_MASTERNS}"
crudini --set $CONF pool_target:${DESIGNATE_POOLMAN_TARGETS} port "${DESIGNATE_DNS_PORT}"

crudini --set $CONF pool_nameserver:${DESIGNATE_POOLMAN_NSS} host "${DESIGNATE_MASTERNS}"
crudini --set $CONF pool_nameserver:${DESIGNATE_POOLMAN_NSS} port "${DESIGNATE_DNS_PORT}"

exec /usr/bin/designate-pool-manager
