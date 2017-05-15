#!/bin/bash

# Create log dir for dragonflow logs
LOG_DIR="/var/log/kolla/dragonflow"
if [[ ! -d "${LOG_DIR}" ]]; then
    mkdir -p ${LOG_DIR}
fi
if [[ $(stat -c %a ${LOG_DIR}) != "755" ]]; then
    chmod 755 ${LOG_DIR}
fi

. /usr/local/bin/kolla_dragonflow_extend_start
