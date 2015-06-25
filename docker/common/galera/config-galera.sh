#!/bin/bash

function configure_files {
    crudini --set $CFG mariadb bind-address "${DB_CLUSTER_BIND_ADDRESS}"
    crudini --set $CFG mariadb binlog_format "ROW"
    crudini --set $CFG mariadb character-set-server "utf8"
    crudini --set $CFG mariadb collation-server "utf8_general_ci"
    crudini --set $CFG mariadb datadir "/var/lib/mysql"
    crudini --set $CFG mariadb default-storage-engine "innodb"
    crudini --set $CFG mariadb init-connect "'SET NAMES utf8'"
    crudini --set $CFG mariadb innodb_autoinc_lock_mode "2"
    crudini --set $CFG mariadb innodb_file_per_table 1
    crudini --set $CFG mariadb innodb_flush_log_at_trx_commit "2"
    crudini --set $CFG mariadb innodb_locks_unsafe_for_binlog "1"
    crudini --set $CFG mariadb innodb_log_file_size "100M"
    crudini --set $CFG mariadb query_cache_size "0"
    crudini --set $CFG mariadb query_cache_type "0"
    crudini --set $CFG mariadb wsrep_cluster_address "gcomm://${DB_CLUSTER_NODES}"
    crudini --set $CFG mariadb wsrep_cluster_name "${DB_CLUSTER_NAME}"
    crudini --set $CFG mariadb wsrep_provider "/usr/lib64/galera/libgalera_smm.so"
    crudini --set $CFG mariadb wsrep_sst_auth "'root:${DB_ROOT_PASSWORD}'"
    crudini --set $CFG mariadb wsrep_sst_method "${DB_CLUSTER_WSREP_METHOD}"
}

function bootstrap_db {
    mysqld_safe --wsrep-new-cluster &

    # Waiting for deamon
    sleep 10
    expect -c '
    set timeout 10
    spawn mysql_secure_installation
    expect "Enter current password for root (enter for none):"
    send "\r"
    expect "Set root password?"
    send "y\r"
    expect "New password:"
    send "'"${DB_ROOT_PASSWORD}"'\r"
    expect "Re-enter new password:"
    send "'"${DB_ROOT_PASSWORD}"'\r"
    expect "Remove anonymous users?"
    send "y\r"
    expect "Disallow root login remotely?"
    send "n\r"
    expect "Remove test database and access to it?"
    send "y\r"
    expect "Reload privilege tables now?"
    send "y\r"
    expect eof'

    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysqladmin -p"${DB_ROOT_PASSWORD}" shutdown
}

function configure_db {
    bootstrap_db

    echo "GRANT ALL ON *.* TO 'root'@'%' IDENTIFIED BY '$DB_ROOT_PASSWORD' ;" > $DB_CLUSTER_INIT_SQL

    if [ "$MARIADB_DATABASE" ]; then
        echo "CREATE DATABASE IF NOT EXISTS $MARIADB_DATABASE ;" >> $DB_CLUSTER_INIT_SQL
    fi

    if [ "$MARIADB_USER" -a "$MARIADB_PASSWORD" ]; then
        echo "CREATE USER '$MARIADB_USER'@'%' IDENTIFIED BY '$MARIADB_PASSWORD' ;" >> $DB_CLUSTER_INIT_SQL

        if [ "$MARIADB_DATABASE" ]; then
            echo "GRANT ALL ON $MARIADB_DATABASE.* TO '$MARIADB_USER'@'%' ;" >> $DB_CLUSTER_INIT_SQL
        fi
    fi

    echo "FLUSH PRIVILEGES" >> $DB_CLUSTER_INIT_SQL
}

function populate_db {
    if [[ $(ls /var/lib/mysql) == "" ]]; then
        echo "POPULATING NEW DB"
        mysql_install_db
        chown -R mysql: /var/lib/mysql
    else
        echo "DB ALREADY EXISTS"
    fi
}

function prepare_db {
    populate_db
    configure_db
    configure_files
}
