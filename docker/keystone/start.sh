#!/bin/bash

set -o errexit

# Loading common functions
source /opt/kolla/kolla-common.sh

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
fi

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "keystone-manage db_sync" keystone
    # Start the api to set initial endpoint and users with the admin_token
    $CMD
    sleep 5

    openstack service create --name keystone --description "OpenStack Identity" identity
    openstack endpoint create --region "${REGION_NAME}" \
                                --publicurl "${PUBLIC_URL}" \
                                --internalurl "${INTERNAL_URL}" \
                                --adminurl "${ADMIN_URL}" \
                                identity
    openstack project create --description "Admin Project" admin
    openstack user create --password "${KEYSTONE_ADMIN_PASSWORD}" admin
    openstack role create admin
    openstack role add --project admin --user admin admin
    exit 0
fi

ARGS="-DFOREGROUND"
echo "Running command: ${CMD} ${ARGS}"
exec $CMD $ARGS
