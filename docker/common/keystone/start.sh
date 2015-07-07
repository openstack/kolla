#!/bin/bash

set -o errexit

CMD="/usr/sbin/httpd"
ARGS="-DFOREGROUND"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "keystone-manage db_sync" keystone

    # Start the api to set initial endpoint and users with the admin_token
    $CMD
    sleep 5

    keystone service-create --name keystone --type identity \
                                --description "OpenStack Identity"
    keystone endpoint-create --region "${REGION_NAME}" \
                                --publicurl "${PUBLIC_URL}" \
                                --internalurl "${INTERNAL_URL}" \
                                --adminurl "${ADMIN_URL}" \
                                --service-id $(keystone service-list | awk '/ identity / {print $2}')

    keystone tenant-create --description "Admin Project" --name admin
    keystone user-create --pass "${KEYSTONE_ADMIN_PASSWORD}" --name admin
    keystone role-create --name admin
    keystone user-role-add --user admin --tenant admin --role admin

    exit 0
fi

exec $CMD $ARGS
