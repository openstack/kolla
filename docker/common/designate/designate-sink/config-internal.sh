#!/bin/bash
set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-designate.sh

CONF=/etc/designate/designate.conf

configure_nova_handler() {
    local DOMAIN_ID=$1

    crudini --set $CONF handler:nova_fixed domain_id "$DOMAIN_ID"
    crudini --set $CONF handler:nova_fixed notification_topics "notifications"
    crudini --set $CONF handler:nova_fixed control_exchange "nova"
    # Configuring multiple record formats
    for FORMAT in $DESIGNATE_SINK_NOVA_FORMATS; do
        crudini --set $CONF handler:nova_fixed format "$FORMAT"
    done
}

configure_neutron_handler() {
    local DOMAIN_ID=$1

    crudini --set $CONF handler:neutron_floatingip domain_id "$DOMAIN_ID"
    crudini --set $CONF handler:neutron_floatingip notification_topics "notifications"
    crudini --set $CONF handler:neutron_floatingip control_exchange "neutron"
    # Configuring multiple record formats
    for FORMAT in $DESIGNATE_SINK_NEUTRON_FORMATS; do
        crudini --set $CONF handler:neutron_floatingip format "$FORMAT"
    done
}

check_required_vars DESIGNATE_API_SERVICE_HOST \
                    DESIGNATE_API_SERVICE_PORT \
                    DESIGNATE_DEFAULT_POOL_NS_RECORD

check_for_os_service_endpoint designate DESIGNATE_API_SERVICE_HOST DESIGNATE_API_SERVICE_PORT || exit $?

if [ -z "$DESIGNATE_SINK_NOVA_DOMAIN_NAME" && -z "$DESIGNATE_SINK_NEUTRON_DOMAIN_NAME" ]; then
    echo "Please specify either Nova or Neutron domain name for Designate Sink"
    exit 1
fi

designate server-create --name ${DESIGNATE_DEFAULT_POOL_NS_RECORD}
if [ $? != 0 ]; then
    echo "Creating server failed" 1>&2
    exit 1
fi

if [ -n "$DESIGNATE_SINK_NOVA_DOMAIN_NAME" ]; then
    NOVA_DOMAIN_ID=$(get_or_create_domain $DESIGNATE_SINK_NOVA_DOMAIN_NAME)
    configure_nova_handler $NOVA_DOMAIN_ID
    HANDLERS="nova_fixed"
fi

if [ -n "$DESIGNATE_SINK_NEUTRON_DOMAIN_NAME" ]; then
    NEUTRON_DOMAIN_ID=$(get_or_create_domain $DESIGNATE_SINK_NEUTRON_DOMAIN_NAME)
    configure_neutron_handler $NEUTRON_DOMAIN_ID
    [ -n "$HANDLERS" ] && HANDLERS+=","
    HANDLERS+="neutron_floatingip"
fi

crudini --set $CONF service:sink enabled_notification_handlers "$HANDLERS"

exec /usr/bin/designate-sink
