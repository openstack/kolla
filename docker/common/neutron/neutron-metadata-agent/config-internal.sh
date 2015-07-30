#!/bin/bash

set -e

. /opt/kolla/config-neutron.sh

check_required_vars ADMIN_TENANT_NAME \
                    DEBUG_LOGGING \
                    KEYSTONE_AUTH_PROTOCOL \
                    KEYSTONE_PUBLIC_SERVICE_HOST \
                    NEUTRON_KEYSTONE_PASSWORD \
                    NEUTRON_KEYSTONE_USER \
                    NEUTRON_SHARED_SECRET \
                    NOVA_METADATA_API_SERVICE_HOST \
                    NOVA_METADATA_API_SERVICE_PORT \
                    VERBOSE_LOGGING

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
        endpoint_type \
        "${ENDPOINT_TYPE}"
crudini --set $cfg \
        DEFAULT \
        auth_url \
        "${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_PUBLIC_SERVICE_HOST}:${KEYSTONE_PUBLIC_SERVICE_PORT}/v2.0"
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
        "${NOVA_METADATA_API_SERVICE_HOST}"
crudini --set $cfg \
        DEFAULT \
        nova_metadata_port \
        "${NOVA_METADATA_API_SERVICE_PORT}"
crudini --set $cfg \
        DEFAULT \
        metadata_proxy_shared_secret \
        "${NEUTRON_SHARED_SECRET}"

# Start Metadata Agent
exec /usr/bin/neutron-metadata-agent --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/metadata_agent.ini --config-dir /etc/neutron
