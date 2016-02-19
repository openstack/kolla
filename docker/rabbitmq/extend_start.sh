#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo chown -R rabbitmq: /var/lib/rabbitmq
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
