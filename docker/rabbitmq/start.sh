#!/bin/sh

set -e

: ${RABBITMQ_USER:=guest}
: ${RABBITMQ_PASS:=guest}
: ${RABBITMQ_NODENAME:=rabbit}
: ${RABBITMQ_LOG_BASE:=/var/log/rabbitmq}

sed -i '
	s|@RABBITMQ_USER@|'"$RABBITMQ_USER"'|g
	s|@RABBITMQ_PASS@|'"$RABBITMQ_PASS"'|g
' /etc/rabbitmq/rabbitmq.config

sed -i '
	s|@RABBITMQ_NODENAME@|'"$RABBITMQ_NODENAME"'|g
	s|@RABBITMQ_LOG_BASE@|'"$RABBITMQ_LOG_BASE"'|g
' /etc/rabbitmq/rabbitmq-env.conf

exec /usr/sbin/rabbitmq-server
