#!/bin/bash

function bootstrap_db {
    mysqld_safe --wsrep-new-cluster &
    # Wait for the mariadb server to be "Ready" before starting the security reset with a max timeout
    # NOTE(huikang): the location of mysql's socket file varies depending on the OS distributions.
    # Querying the cluster status has to be executed after the existence of mysql.sock and mariadb.pid.
    TIMEOUT=${DB_MAX_TIMEOUT:-60}
    while [[ ! -S /var/lib/mysql/mysql.sock ]] && \
          [[ ! -S /var/run/mysqld/mysqld.sock ]] || \
          [[ ! -f /var/lib/mysql/mariadb.pid ]]; do
        if [[ ${TIMEOUT} -gt 0 ]]; then
            let TIMEOUT-=1
            sleep 1
        else
            exit 1
        fi
    done
# NOTE(sbezverk): Currently kolla-kubernetes does not use Galera and disables wsrep driver.
# This check will run only for non kolla-kubernetes bootstrap deployments.
    if [[ ! "${!KOLLA_KUBERNETES[@]}" ]]; then
        CLUSTER_READY=$(mysql -u root --exec="SHOW STATUS LIKE 'wsrep_cluster_status'" | grep Primary)
        TIMEOUT=${DB_MAX_TIMEOUT:-60}
        while [[ -z "${CLUSTER_READY}" ]]; do
            if [[ ${TIMEOUT} -gt 0 ]]; then
                let TIMEOUT-=1
                sleep 1
            else
                exit 1
            fi
        done
    fi
    sudo -E kolla_security_reset
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysqladmin -uroot -p"${DB_ROOT_PASSWORD}" shutdown
}

# Only update permissions if permissions need to be updated
if [[ $(stat -c %U:%G /var/lib/mysql) != "mysql:mysql" ]]; then
    sudo chown mysql: /var/lib/mysql
fi

# Create log directory, with appropriate permissions
if [[ ! -d "/var/log/kolla/mariadb" ]]; then
    mkdir -p /var/log/kolla/mariadb
fi
if [[ $(stat -c %a /var/log/kolla/mariadb) != "755" ]]; then
    chmod 755 /var/log/kolla/mariadb
fi

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    mysql_install_db
    bootstrap_db
    exit 0
fi

if [[ "${!BOOTSTRAP_ARGS[@]}" ]]; then
    ARGS="${BOOTSTRAP_ARGS}"
fi
