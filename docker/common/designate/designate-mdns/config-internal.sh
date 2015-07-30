#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-designate.sh

check_required_vars DESIGNATE_MASTERNS \
                    DESIGNATE_MDNS_PORT

CONF=/etc/designate/designate.conf

crudini --set $CONF service:mdns workers "1"
crudini --set $CONF service:mdns host "${DESIGNATE_MASTERNS}"
crudini --set $CONF service:mdns port "${DESIGNATE_MDNS_PORT}"
crudini --set $CONF service:mdns tcp_backlog "100"
crudini --set $CONF service:mdns all_tcp "False"

exec /usr/bin/designate-mdns
