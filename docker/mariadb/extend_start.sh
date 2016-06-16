#!/bin/bash

function bootstrap_db {
    mysqld_safe --wsrep-new-cluster &
    # Wait for the mariadb server to be "Ready" before starting the security reset with a max timeout
    TIMEOUT=${DB_MAX_TIMEOUT:-60}
    while [[ ! -f /var/lib/mysql/mariadb.pid ]]; do
        if [[ ${TIMEOUT} -gt 0 ]]; then
            let TIMEOUT-=1
            sleep 1
        else
            exit 1
        fi
    done
    sudo -E kolla_security_reset
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysqladmin -uroot -p"${DB_ROOT_PASSWORD}" shutdown
}

function kolla_kubernetes {
    KUBE_TOKEN=$(</var/run/secrets/kubernetes.io/serviceaccount/token)
    bootstrap_url=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCPORT/api/v1/namespaces/default/pods | grep /api/v1/namespaces/default/pods/mariadb-bootstrap | cut -d '"' -f 4) || true
    MARIADB_BOOTSTRAPPED=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCPORT$bootstrap_url | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["status"]["phase"]') || MARIADB_BOOTSTRAPPED='Succeeded'

    if [[ "$MARIADB_BOOTSTRAPPED" != "Succeeded" ]]; then
        echo "Mariadb bootstrapping isn't complete"
        exit 1
    fi
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

#***** KOLLA-KUBERNETES *****
# TODO: Add a kolla_kubernetes script at build time when templating is complete
if [[ "${!KOLLA_KUBERNETES[@]}" ]]; then
    kolla_kubernetes
fi
#***** KOLLA-KUBERNETES *****
