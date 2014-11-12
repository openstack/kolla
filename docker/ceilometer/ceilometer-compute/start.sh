#!/bin/sh

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-ceilometer.sh


check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_SERVICE_HOST KEYSTONE_AUTH_PROTOCOL CEILOMETER_KEYSTONE_USER ADMIN_TENANT_NAME

check_for_keystone

# Nova conf settings
crudini --set /etc/nova/nova.conf DEFAULT instance_usage_audit True
crudini --set /etc/nova/nova.conf DEFAULT instance_usage_audit_period hour
crudini --set /etc/nova/nova.conf DEFAULT notify_on_state_change vm_and_task_state
crudini --set /etc/nova/nova.conf DEFAULT notification_driver nova.openstack.common.notifier.rpc_notifier
crudini --set /etc/nova/nova.conf DEFAULT notification_driver ceilometer.compute.nova_notifier

#ceilometer settings
cfg=/etc/ceilometer/ceilometer.conf
crudini --set $cfg publisher_rpc metering_secret ${KEYSTONE_ADMIN_TOKEN}
crudini --set $cfg rabbit_host ${KEYSTONE_SERVICE_HOST}
crudini --set $cfg rabbit_password ${RABBITMQ_PASS}


exec /usr/bin/ceilometer-agent-compute
