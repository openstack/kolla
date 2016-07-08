#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo chown -R rabbitmq: /var/lib/rabbitmq

# NOTE(sbezverk): In kubernetes environment, if this file exists from previous
# bootstrap, the system does not allow to overwrite it (it bootstrap files with
# permission denied error) but it allows to delete it and then recreate it.
    if [[ -e "/var/lib/rabbitmq/.erlang.cookie" ]]; then
        rm -f /var/lib/rabbitmq/.erlang.cookie
    fi
    echo "${RABBITMQ_CLUSTER_COOKIE}" > /var/lib/rabbitmq/.erlang.cookie
    chmod 400 /var/lib/rabbitmq/.erlang.cookie
    exit 0
fi

if [[ ! -d "/var/log/kolla/rabbitmq" ]]; then
    mkdir -p /var/log/kolla/rabbitmq
fi
if [[ $(stat -c %a /var/log/kolla/rabbitmq) != "755" ]]; then
    chmod 755 /var/log/kolla/rabbitmq
fi
