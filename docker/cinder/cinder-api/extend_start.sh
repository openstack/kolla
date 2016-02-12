#!/bin/bash
set -o errexit

if [[ ! -d "/var/log/kolla/cinder" ]]; then
    mkdir -p /var/log/kolla/cinder
fi
if [[ $(stat -c %a /var/log/kolla/cinder) != "755" ]]; then
    chmod 755 /var/log/kolla/cinder
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    cinder-manage db sync
    exit 0
fi
