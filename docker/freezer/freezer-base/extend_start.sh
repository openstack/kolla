#!/bin/bash

# Create log dir for freezer logs
LOG_DIR="/var/log/kolla/freezer"
if [[ ! -d "${LOG_DIR}" ]]; then
    mkdir -p ${LOG_DIR}
fi
if [[ $(stat -c %U:%G ${LOG_DIR}) != "freezer:kolla" ]]; then
    chown freezer:kolla ${LOG_DIR}
fi
if [[ $(stat -c %a ${LOG_DIR}) != "755" ]]; then
    chmod 755 ${LOG_DIR}
fi

. /usr/local/bin/kolla_freezer_extend_start
