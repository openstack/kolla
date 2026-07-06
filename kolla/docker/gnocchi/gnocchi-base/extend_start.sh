#!/bin/bash

# Create log dir for Gnocchi logs
GNOCCHI_LOG_DIR="/var/log/kolla/gnocchi"
if [[ ! -d "${GNOCCHI_LOG_DIR}" ]]; then
    mkdir -p ${GNOCCHI_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${GNOCCHI_LOG_DIR}) != "gnocchi:kolla" ]]; then
    chown gnocchi:kolla ${GNOCCHI_LOG_DIR}
fi
if [[ $(stat -c %a ${GNOCCHI_LOG_DIR}) != "755" ]]; then
    chmod 755 ${GNOCCHI_LOG_DIR}
fi

. /usr/local/bin/kolla_gnocchi_extend_start
