#!/bin/sh

: ${RABBITMQ_USER:=guest}
: ${RABBITMQ_PASS:=guest}
: ${RABBITMQ_NODE_PORT:=5672}
: ${RABBITMQ_LOG_BASE:=/var/log/rabbitmq}

sed -i '
	s|@RABBITMQ_USER@|'"$RABBITMQ_USER"'|g
	s|@RABBITMQ_PASS@|'"$RABBITMQ_PASS"'|g
' /etc/rabbitmq/rabbitmq.config

sed -i '
	s|@RABBITMQ_PORT@|'"$RABBITMQ_NODE_PORT"'|g
	s|@RABBITMQ_LOG_BASE@|'"$RABBITMQ_LOG_BASE"'|g
' /etc/rabbitmq/rabbitmq-env.conf

exec /usr/lib/rabbitmq/bin/rabbitmq-server

