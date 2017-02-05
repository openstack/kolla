#!/bin/bash

PANKO_LOG_DIR=/var/log/kolla/panko

if [[ ! -d "${PANKO_LOG_DIR}" ]]; then
    mkdir -p ${PANKO_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${PANKO_LOG_DIR}) != "panko:kolla" ]]; then
    chown panko:kolla ${PANKO_LOG_DIR}
fi
if [[ $(stat -c %a ${PANKO_LOG_DIR}) != "755" ]]; then
    chmod 755 ${PANKO_LOG_DIR}
fi

. /usr/local/bin/kolla_panko_extend_start
