#!/bin/bash
SOURCE="/opt/kolla/mariadb/galera.cnf"
TARGET="/etc/my.cnf.d/galera.cnf"
OWNER="mysql"

# Cluster configuration
if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0600 $TARGET
fi
