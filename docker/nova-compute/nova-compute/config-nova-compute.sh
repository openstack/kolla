#!/bin/sh

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-nova.sh

cfg=/etc/nova/nova.conf

check_required_vars NOVA_COMPUTE_LOG_FILE

# configure logging
crudini --set $cfg DEFAULT log_file "${NOVA_COMPUTE_LOG_FILE}"

# set qmeu emulation if no hardware acceleration found
if [[ `egrep -c '(vmx|svm)' /proc/cpuinfo` == 0 ]]
then
    crudini --set $cfg libvirt virt_type qemu
fi

mkdir -p /var/lib/nova/instances
