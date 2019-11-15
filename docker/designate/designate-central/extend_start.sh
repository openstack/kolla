#!/bin/bash

if [[ ! -f "/var/log/kolla/designate/designate-manage.log" ]]; then
    touch /var/log/kolla/designate/designate-manage.log
    chmod 644 /var/log/kolla/designate/designate-manage.log
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    designate-manage database sync
    exit 0
fi
