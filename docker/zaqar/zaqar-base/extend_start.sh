#!/bin/bash

# Create log dir for Zaqar logs
LOG_DIR="/var/log/kolla/zaqar"
if [[ ! -d "${LOG_DIR}" ]]; then
    mkdir -p ${LOG_DIR}
fi
if [[ $(stat -c %U:%G ${LOG_DIR}) != "zaqar:kolla" ]]; then
    chown zaqar:kolla ${LOG_DIR}
fi
if [[ $(stat -c %a ${LOG_DIR}) != "755" ]]; then
    chmod 755 ${LOG_DIR}
fi

. /usr/local/bin/kolla_zaqar_extend_start
