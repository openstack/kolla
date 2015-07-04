#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-rabbit.sh

check_required_vars RABBITMQ_PASS RABBITMQ_USER

configure_rabbit

exec /usr/sbin/rabbitmq-server
