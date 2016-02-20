#!/bin/bash

if [[ ! -d "/var/log/kolla/heat" ]]; then
    mkdir -p /var/log/kolla/heat
fi
if [[ $(stat -c %a /var/log/kolla/heat) != "755" ]]; then
    chmod 755 /var/log/kolla/heat
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    heat-manage db_sync
    openstack domain create heat
    openstack user create --domain heat heat_domain_admin --password ${HEAT_DOMAIN_ADMIN_PASSWORD}
    openstack role add --domain heat --user heat_domain_admin admin
    openstack role create heat_stack_owner
    openstack role create heat_stack_user
    exit 0
fi
