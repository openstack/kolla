#!/bin/bash

function bootstrap_db {
    mysqld_safe --wsrep-new-cluster &

    # Waiting for deamon
    sleep 10
    kolla_security_reset

    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysqladmin -p"${DB_ROOT_PASSWORD}" shutdown
}

chown mysql: /var/lib/mysql

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]] && [[ ! -e /var/lib/mysql/cluster.exists ]]; then
    ARGS="--wsrep-new-cluster"
    touch /var/lib/mysql/cluster.exists
    mysql_install_db --user=mysql
    bootstrap_db
fi
