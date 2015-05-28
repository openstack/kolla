#!/bin/bash

. /opt/kolla/kolla-common.sh

: ${BIND_ADDRESS:=$PUBLIC_IP}
: ${DB_ROOT_PASSWORD:=$DB_ROOT_PASSWORD}
: ${DEFAULT_STORAGE_ENGINE:=innodb}
: ${COLLATION_SERVER:=utf8_general_ci}
: ${INIT_CONNECT:=SET NAMES utf8}
: ${CHAR_SET_SERVER:=utf8}
: ${INNODB_FILE_PER_TABLE:=true}
: ${DATADIR:=/var/lib/mysql}
: ${TEMP_FILE:='/tmp/mysql-first-time.sql'}

server_cnf=/etc/my.cnf.d/server.cnf

crudini --set $server_cnf mysqld bind-address $BIND_ADDRESS
crudini --set $server_cnf mysqld default-storage-engine $DEFAULT_STORAGE_ENGINE
crudini --set $server_cnf mysqld collation-server $COLLATION_SERVER
crudini --set $server_cnf mysqld init-connect "'${INIT_CONNECT}'"
crudini --set $server_cnf mysqld character-set-server $CHAR_SET_SERVER
if [ "${INNODB_FILE_PER_TABLE}" == "true" ] || ["${INNODB_FILE_PER_TABLE}" == "True" ] ; then
    crudini --set $server_cnf mysqld innodb_file_per_table 1
fi
