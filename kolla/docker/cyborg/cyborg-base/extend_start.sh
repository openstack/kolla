#!/bin/bash

# Create log dir for Cyborg logs
CYBORG_LOG_DIR="/var/log/kolla/cyborg"
if [[ ! -d "${CYBORG_LOG_DIR}" ]]; then
    mkdir -p ${CYBORG_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${CYBORG_LOG_DIR}) != "cyborg:kolla" ]]; then
    chown cyborg:kolla ${CYBORG_LOG_DIR}
fi
if [[ $(stat -c %a ${CYBORG_LOG_DIR}) != "755" ]]; then
    chmod 755 ${CYBORG_LOG_DIR}
fi

. /usr/local/bin/kolla_cyborg_extend_start
