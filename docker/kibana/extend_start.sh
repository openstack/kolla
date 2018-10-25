#!/bin/bash

KIBANA_LOG_DIR="/var/log/kolla/kibana"

if [[ ! -d "${KIBANA_LOG_DIR}" ]]; then
    mkdir -p "${KIBANA_LOG_DIR}"
fi
if [[ $(stat -c %U:%G "${KIBANA_LOG_DIR}") != "kibana:kolla" ]]; then
    chown kibana:kolla "${KIBANA_LOG_DIR}"
fi
