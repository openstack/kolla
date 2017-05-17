#!/bin/bash

rm -f /var/run/chronyd.pid

CHRONY_LOG_DIR="/var/log/kolla/chrony"
if [[ ! -d "${CHRONY_LOG_DIR}" ]]; then
    mkdir -p ${CHRONY_LOG_DIR}
fi

if [[ $(stat -c %a ${CHRONY_LOG_DIR}) != "755" ]]; then
    chmod 755 /var/log/kolla/chrony
fi

if [[ $(stat -c %U:%G ${CHRONY_LOG_DIR}) != "chrony:chrony" ]]; then
    chown chrony:chrony ${CHRONY_LOG_DIR}
fi
