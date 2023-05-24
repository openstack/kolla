#!/bin/bash

: ${MARIADB_LOG_DIR:=/var/log/kolla/mariadb}

# Create log directory, with appropriate permissions
if [[ ! -d "${MARIADB_LOG_DIR}" ]]; then
    mkdir -p ${MARIADB_LOG_DIR}
fi
if [[ $(stat -c %a ${MARIADB_LOG_DIR}) != "755" ]]; then
    chmod 755 ${MARIADB_LOG_DIR}
fi
