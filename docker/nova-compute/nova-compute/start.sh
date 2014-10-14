#!/bin/sh

. /opt/kolla/kolla-common.sh

: ${NOVA_KEYSTONE_USER:=nova}
: ${ADMIN_TENANT_NAME:=admin}

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_SERVICE_HOST

cfg=/etc/nova/nova.conf

crudini --set $cfg DEFAULT admin_token "${KEYSTONE_ADMIN_TOKEN}"
crudini --sel $cfg DEFAULT log_file ""
crudini --del $cfg  DEFAULT log_dir
crudini --set $cfg DEFAULT use_stderr True
crudini --set $cfg \
    libvirt \
    connection_uri \
    "qemu+tcp://${NOVA_PORT_16509_TCP_PORT}/system"

for option in auth_protocol auth_host auth_port; do
    crudini --del $cfg \
        keystone_authtoken \
        $option
done

crudini --set $cfg \
    keystone_authtoken \
    auth_uri \
    "http://${KEYSTONE_SERVICE_HOST}:5000/"
crudini --set $cfg \
    keystone_authtoken \
    admin_tenant_name \
    "${ADMIN_TENANT_NAME}"
crudini --set $cfg \
    keystone_authtoken \
    admin_user \
    "${NOVA_KEYSTONE_USER}"
crudini --set $cfg \
    keystone_authtoken \
    admin_password \
    "${NOVA_KEYSTONE_PASSWORD}"

exec /usr/bin/nova-compute
