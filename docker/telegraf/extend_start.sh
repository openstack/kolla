#!/bin/bash

TELEGRAF_LOG_DIR="/var/log/kolla/telegraf"

if [[ ! -d "${TELEGRAF_LOG_DIR}" ]]; then
    mkdir -p ${TELEGRAF_LOG_DIR}
fi
if [[ $(stat -c %a ${TELEGRAF_LOG_DIR}) != "755" ]]; then
    chmod 755 ${TELEGRAF_LOG_DIR}
fi
