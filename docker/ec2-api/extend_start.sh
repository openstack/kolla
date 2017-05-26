#!/bin/bash

if [[ ! -d "/var/log/kolla/ec2-api" ]]; then
    mkdir -p /var/log/kolla/ec2-api
fi
if [[ $(stat -c %a /var/log/kolla/ec2-api) != "755" ]]; then
    chmod 755 /var/log/kolla/ec2-api
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    ec2-api-manage db_sync
    exit 0
fi
