#!/bin/bash

. /opt/kolla/config-rabbit.sh

configure_rabbit

exec /usr/sbin/rabbitmq-server
