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

echo "Starting cinder-backup"
exec /usr/bin/cinder-backup --config-file $cfg
