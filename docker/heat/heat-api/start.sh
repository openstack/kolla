#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/sh -c "heat-manage db_sync" heat
    openstack domain create heat_user_domain
    openstack user create --domain heat_user_domain heat_domain_admin --password ${HEAT_DOMAIN_ADMIN_PASSWORD}
    openstack role add --domain heat_user_domain --user heat_domain_admin admin
    exit 0
fi

exec $CMD
