#!/bin/bash

# Create log dir for Barbican logs
LOG_DIR="/var/log/kolla/barbican"
if [[ ! -d "${LOG_DIR}" ]]; then
    mkdir -p ${LOG_DIR}
fi
if [[ $(stat -c %U:%G ${LOG_DIR}) != "barbican:kolla" ]]; then
    chown barbican:kolla ${LOG_DIR}
fi
if [[ $(stat -c %a ${LOG_DIR}) != "755" ]]; then
    chmod 755 ${LOG_DIR}
fi

. /usr/local/bin/kolla_barbican_extend_start
