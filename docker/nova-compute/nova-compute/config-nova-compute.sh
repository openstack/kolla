#!/bin/sh

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-nova.sh

check_required_vars NOVA_LIBVIRT_SERVICE_HOST

cfg=/etc/nova/nova.conf

crudini --set $cfg libvirt virt_type kvm
crudini --set $cfg libvirt \
    connection_uri qemu+tcp://${NOVA_LIBVIRT_SERVICE_HOS}/system

