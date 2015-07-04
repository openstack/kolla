#!/bin/bash

# Cluster configuration
if [[ -f /opt/kolla/rabbitmq/rabbitmq.config ]]; then
    cp -af /opt/kolla/rabbitmq/rabbitmq.config /etc/rabbitmq/rabbitmq.config
    chown rabbitmq: /etc/rabbitmq/rabbitmq.config
    chmod 0600 /etc/rabbitmq/rabbitmq.config
fi

if [[ -f /opt/kolla/rabbitmq/rabbitmq-env.conf ]]; then
    cp -af /opt/kolla/rabbitmq/rabbitmq-env.conf /etc/rabbitmq/rabbitmq-env.conf
    chown rabbitmq: /etc/rabbitmq/rabbitmq-env.conf
    chmod 0600 /etc/rabbitmq/rabbitmq-env.conf
fi
