#!/bin/sh

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-nova.sh

cfg=/etc/nova/nova.conf

# set qmeu emulation if no hardware acceleration found
if [[ `egrep -c '(vmx|svm)' /proc/cpuinfo` == 0 ]]
then
    crudini --set $cfg libvirt virt_type qemu
fi

mkdir -p /var/lib/nova/instances
