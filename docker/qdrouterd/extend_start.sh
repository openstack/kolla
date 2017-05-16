#!/bin/bash

# Create log directory, with appropriate permissions
QDROUTERD_LOG_DIR="/var/log/kolla/qdrouterd"
if [[ ! -d "${QDROUTERD_LOG_DIR}" ]]; then
    mkdir -p ${QDROUTERD_LOG_DIR}
fi
if [[ $(stat -c %a ${QDROUTERD_LOG_DIR}) != "755" ]]; then
    chmod 755 ${QDROUTERD_LOG_DIR}
fi
