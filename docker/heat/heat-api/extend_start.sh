#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    heat-manage db_sync
    CURRENT_HEAT_DOMAIN_NAME=$(openstack domain list | grep heat | awk '{print $4}')

    if [[ "heat_user_domain" != "$CURRENT_HEAT_DOMAIN_NAME" ]]; then
        openstack domain create heat_user_domain
        openstack user create --domain heat_user_domain heat_domain_admin --password ${HEAT_DOMAIN_ADMIN_PASSWORD}
        openstack role add --domain heat_user_domain --user heat_domain_admin admin
        openstack role create heat_stack_owner
        openstack role create heat_stack_user
    fi
    exit 0
fi
