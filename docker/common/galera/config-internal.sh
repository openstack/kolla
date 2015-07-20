#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-galera.sh

check_required_vars DB_CLUSTER_BIND_ADDRESS \
                    DB_CLUSTER_INIT_DB \
                    DB_CLUSTER_NAME \
                    DB_CLUSTER_NODES \
                    DB_CLUSTER_WSREP_METHOD \
                    DB_ROOT_PASSWORD

CFG=/etc/my.cnf.d/server.cnf
DB_CLUSTER_INIT_SQL=/tmp/mysql-first-time.sql

prepare_db

if [[ "${DB_CLUSTER_INIT_DB}" == "true" ]] && ! [[ -a /var/lib/mysql/cluster.exists ]]; then
    DB_CLUSTER_IS_MASTER_NODE="--wsrep-new-cluster"
    touch /var/lib/mysql/cluster.exists
fi

mysqld_safe --init-file=$DB_CLUSTER_INIT_SQL $DB_CLUSTER_IS_MASTER_NODE
