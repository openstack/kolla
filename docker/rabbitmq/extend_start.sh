#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    echo "${RABBITMQ_CLUSTER_COOKIE}" > /var/lib/rabbitmq/.erlang.cookie
    chown -R rabbitmq: /var/lib/rabbitmq
    chmod 400 /var/lib/rabbitmq/.erlang.cookie
    exit 0
fi
