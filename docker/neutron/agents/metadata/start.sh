#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh
. /sudoers.sh

: ${KEYSTONE_REGION:=RegionOne}

check_required_vars VERBOSE_LOGGING DEBUG_LOGGING KEYSTONE_AUTH_PROTOCOL \
                    KEYSTONE_PUBLIC_SERVICE_HOST ADMIN_TENANT_NAME \
                    NEUTRON_KEYSTONE_USER NEUTRON_KEYSTONE_PASSWORD \
                    NEUTRON_SHARED_SECRET NOVA_API_SERVICE_HOST \
                    NEUTRON_METADATA_AGENT_LOG_FILE

cfg=/etc/neutron/metadata_agent.ini
neutron_conf=/etc/neutron/neutron.conf

# Logging
crudini --set $neutron_conf \
        DEFAULT \
        log_file \
        "${NEUTRON_METADATA_AGENT_LOG_FILE}"

# Configure metadata_agent.ini
crudini --set $cfg \
        DEFAULT \
        verbose \
        "${VERBOSE_LOGGING}"
crudini --set $cfg \
        DEFAULT \
        debug \
        "${DEBUG_LOGGING}"
crudini --set $cfg \
        DEFAULT \
        auth_region \
        "${KEYSTONE_REGION}"
crudini --set $cfg \
        DEFAULT \
        auth_url \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
crudini --set $cfg \
        DEFAULT \
        admin_tenant_name \
        "${ADMIN_TENANT_NAME}"
crudini --set $cfg \
        DEFAULT \
        admin_user \
        "${NEUTRON_KEYSTONE_USER}"
crudini --set $cfg \
        DEFAULT \
        admin_password \
        "${NEUTRON_KEYSTONE_PASSWORD}"
crudini --set $cfg \
        DEFAULT \
        nova_metadata_ip \
        "${NOVA_API_SERVICE_HOST}"
crudini --set $cfg \
        DEFAULT \
        metadata_proxy_shared_secret \
        "${NEUTRON_SHARED_SECRET}"

# Start Metadata Agent
exec /usr/bin/neutron-metadata-agent
