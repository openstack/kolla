#!/bin/bash

# Create log dir for Aodh logs
AODH_LOG_DIR="/var/log/kolla/aodh"
if [[ ! -d "${AODH_LOG_DIR}" ]]; then
    mkdir -p ${AODH_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${AODH_LOG_DIR}) != "aodh:kolla" ]]; then
    chown aodh:kolla ${AODH_LOG_DIR}
fi
if [[ $(stat -c %a ${AODH_LOG_DIR}) != "755" ]]; then
    chmod 755 ${AODH_LOG_DIR}
fi

. /usr/local/bin/kolla_aodh_extend_start
