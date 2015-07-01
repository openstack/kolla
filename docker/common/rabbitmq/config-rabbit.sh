#!/bin/bash

RABBITMQ_CLUSTER_CONFIGURATION=""

function configure_files {
    sed -i '
        s|@RABBITMQ_USER@|'"$RABBITMQ_USER"'|g
        s|@RABBITMQ_PASS@|'"$RABBITMQ_PASS"'|g
        s|@RABBITMQ_CLUSTER_CONFIGURATION@|'"$RABBITMQ_CLUSTER_CONFIGURATION"'|g
    ' /etc/rabbitmq/rabbitmq.config

    sed -i '
        s|@RABBITMQ_LOG_BASE@|'"$RABBITMQ_LOG_BASE"'|g
    ' /etc/rabbitmq/rabbitmq-env.conf
}

function set_rabbitmq_cookie {
    echo "${RABBITMQ_CLUSTER_COOKIE}" > /var/lib/rabbitmq/.erlang.cookie
    chown rabbitmq: /var/lib/rabbitmq/.erlang.cookie
    chmod 400 /var/lib/rabbitmq/.erlang.cookie
}

function configure_cluster {
    check_required_vars RABBITMQ_CLUSTER_COOKIE RABBITMQ_CLUSTER_NODES
    set_rabbitmq_cookie

    HOSTNAME=""
    IP_ADDRESS=""
    DELIMETER=""

    for node in ${RABBITMQ_CLUSTER_NODES}; do
        HOSTNAME=`echo ${node} | cut -d'@' -f1`
        IP_ADDRESS=`echo ${node} | cut -d'@' -f2`
        CLUSTER_NODES="${CLUSTER_NODES}${DELIMETER}rabbit@${HOSTNAME}"
        echo "${IP_ADDRESS} ${HOSTNAME}" >> /etc/hosts
        DELIMETER=","
    done
    RABBITMQ_CLUSTER_CONFIGURATION="{cluster_nodes, {[$CLUSTER_NODES], disc}},"
}

function configure_rabbit {
    if [ "$RABBITMQ_CLUSTER_NODES" ] && [ "$RABBITMQ_CLUSTER_COOKIE" ]; then
        configure_cluster
    elif [ "$RABBITMQ_SERVICE_HOST" ]; then
        # work around:
        # https://bugs.launchpad.net/ubuntu/+source/rabbitmq-server/+bug/653405
        echo "${RABBITMQ_SERVICE_HOST} `/usr/bin/hostname -s`" > /etc/hosts
    else
        echo "You need RABBITMQ_SERVICE_HOST or RABBITMQ_CLUSTER_NODES & " \
            " RABBITMQ_CLUSTER_COOKIES variables"
        exit 1
    fi

    configure_files
}
