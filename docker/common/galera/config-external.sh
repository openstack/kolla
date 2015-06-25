#!/bin/bash

# Cluster configuration
if [[ -f /opt/kolla/mariadb/galera.cnf ]]; then
    cp /opt/kolla/mariadb/galera.cnf /etc/my.cnf.d/galera.cnf
    chown mysql: /etc/my.cnf.d/galera.cnf
    chmod 0600 /etc/my.cnf.d/galera.cnf
fi
