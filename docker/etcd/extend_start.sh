#!/bin/bash

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/etcd" ]]; then
    mkdir -p /var/log/kolla/etcd
fi
if [[ $(stat -c %a /var/log/kolla/etcd) != "755" ]]; then
    chmod 755 /var/log/kolla/etcd
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo chown etcd: /var/lib/etcd/
    exit 0
fi
