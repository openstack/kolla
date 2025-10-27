#!/bin/bash

: ${MARIADB_LOG_DIR:=/var/log/kolla/mariadb}

function bootstrap_db {
    mariadbd-safe --wsrep-new-cluster --skip-networking --wsrep-on=OFF --pid-file=/var/lib/mysql/mariadb.pid &
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

    sudo -E kolla_security_reset

    set +o xtrace
    mariadb -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mariadb -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mariadb-admin -uroot -p"${DB_ROOT_PASSWORD}" shutdown
    set -o xtrace
}

# Create log directory, with appropriate permissions
if [[ ! -d "${MARIADB_LOG_DIR}" ]]; then
    mkdir -p ${MARIADB_LOG_DIR}
fi
if [[ $(stat -c %a ${MARIADB_LOG_DIR}) != "755" ]]; then
    chmod 755 ${MARIADB_LOG_DIR}
fi

# This catches all cases of the BOOTSTRAP variable being set, including empty
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    mariadb-install-db 2>&1 | tee -a ${MARIADB_LOG_DIR}/mariadb-bootstrap.log
    bootstrap_db 2>&1 | tee -a ${MARIADB_LOG_DIR}/mariadb-bootstrap.log
    exit 0
fi

# This catches all cases of the KOLLA_UPGRADE variable being set, including empty
if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    # The mariadb-upgrade command treats any directories under /var/lib/mysql as
    # databases. Somehow we can end up with a .pki directory, which causes the
    # command to fail with this error:
    # Incorrect database name '#mysql50#.pki' when selecting the database
    # There doesn't seem to be anything in the directory, so remove it.
    rm -rf /var/lib/mysql/.pki

    mariadb-upgrade --host=${DB_HOST} --port=${DB_PORT} --user=root --password="${DB_ROOT_PASSWORD}" 2>&1 | tee -a ${MARIADB_LOG_DIR}/mariadb-upgrade.log
    exit 0
fi

if [[ "${!BOOTSTRAP_ARGS[@]}" ]]; then
    ARGS="${BOOTSTRAP_ARGS}"
fi
