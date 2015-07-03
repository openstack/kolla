#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-cinder.sh

check_required_vars CINDER_BACKUP_DRIVER CINDER_BACKUP_MANAGER \
                    CINDER_BACKUP_API_CLASS CINDER_BACKUP_NAME_TEMPLATE

cfg=/etc/cinder/cinder.conf

# volume backup configuration
crudini --set $cfg \
        DEFAULT \
        backup_driver \
        "${CINDER_BACKUP_DRIVER}"
crudini --set $cfg \
        DEFAULT \
        backup_topic \
        "cinder-backup"
crudini --set $cfg \
        DEFAULT \
        backup_manager \
        "${CINDER_BACKUP_MANAGER}"
crudini --set $cfg \
        DEFAULT \
        backup_api_class \
        "${CINDER_BACKUP_API_CLASS}"
crudini --set $cfg \
        DEFAULT \
        backup_name_template \
        "${CINDER_BACKUP_NAME_TEMPLATE}"

# https://bugs.launchpad.net/kolla/+bug/1461635
# Cinder requires mounting /dev in the cinder-volume, nova-compute,
# and libvirt containers.  If /dev/pts/ptmx does not have proper permissions
# on the host, then libvirt will fail to boot an instance.
# This is a bug in Docker where it is not correctly mounting /dev/pts
# Tech Debt tracker: https://bugs.launchpad.net/kolla/+bug/1468962
# **Temporary fix**
chmod 666 /dev/pts/ptmx

echo "Starting cinder-backup"
exec /usr/bin/cinder-backup --config-file $cfg
