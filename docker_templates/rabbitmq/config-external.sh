#!/bin/bash
SOURCE_CONFIG="/opt/kolla/rabbitmq/rabbitmq.config"
TARGET_CONFIG="/etc/rabbitmq/rabbitmq.config"
SOURCE_ENV="/opt/kolla/rabbitmq/rabbitmq-env.conf"
TARGET_ENV="/etc/rabbitmq/rabbitmq-env.conf"
OWNER="rabbitmq"

# Cluster configuration
if [[ -f "$SOURCE_CONFIG" ]]; then
    cp -af $SOURCE_CONFIG $TARGET_CONFIG
    chown ${OWNER}: $TARGET_CONFIG
    chmod 0600 $TARGET_CONFIG
fi

if [[ -f "$SOURCE_ENV" ]]; then
    cp -af $SOURCE_ENV $TARGET_ENV
    chown ${OWNER}: $TARGET_ENV
    chmod 0600 $TARGET_ENV
fi
