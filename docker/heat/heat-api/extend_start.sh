#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    heat-manage db_sync

    EXISTING_DOMAINS=$(openstack domain list -f value -c Name)

    if ! echo "$EXISTING_DOMAINS" | grep '^heat_user_domain$' &>/dev/null; then
        openstack domain create heat_user_domain
        openstack user create --domain heat_user_domain heat_domain_admin --password ${HEAT_DOMAIN_ADMIN_PASSWORD}
        openstack role add --domain heat_user_domain --user-domain heat_user_domain --user heat_domain_admin admin
    fi

    exit 0
fi

. /usr/local/bin/kolla_httpd_setup
