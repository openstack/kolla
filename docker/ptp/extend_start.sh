#!/bin/bash

rm -f /var/run/ptp.pid

PTP_LOG_DIR="/var/log/kolla/ptp"
if [[ ! -d "${PTP_LOG_DIR}" ]]; then
    mkdir -p ${PTP_LOG_DIR}
fi

if [[ $(stat -c %a ${PTP_LOG_DIR}) != "755" ]]; then
    chmod 755 ${PTP_LOG_DIR}
fi
