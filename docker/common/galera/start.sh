#!/bin/bash

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-galera.sh

check_required_vars DB_CLUSTER_INIT_DB
prepare_db

if [[ "${DB_CLUSTER_INIT_DB}" == "true" ]] && ! [[ -a /var/lib/mysql/cluster.exists ]]; then
    DB_CLUSTER_IS_MASTER_NODE="--wsrep-new-cluster"
    touch /var/lib/mysql/cluster.exists
fi

mysqld_safe --init-file=$DB_CLUSTER_INIT_SQL $DB_CLUSTER_IS_MASTER_NODE

