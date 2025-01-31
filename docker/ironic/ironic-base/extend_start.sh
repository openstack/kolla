#!/bin/bash

LOG_PATH=/var/log/kolla/ironic
METRICS_PATH=/var/lib/ironic-metrics

if [[ ! -d "${LOG_PATH}" ]]; then
    mkdir -p "${LOG_PATH}"
fi
if [[ ! -d "${METRICS_PATH}" ]]; then
    sudo mkdir -p "${METRICS_PATH}"
fi
if [[ $(stat -c %a "${LOG_PATH}") != "755" ]]; then
    chmod 755 "${LOG_PATH}"
fi
if [[ $(stat -c %U:%G "${METRICS_PATH}") != "ironic:ironic" ]]; then
    sudo chown ironic:ironic "${METRICS_PATH}"
fi
if [[ $(stat -c %a "${METRICS_PATH}") != "2775" ]]; then
    sudo chmod 2775 "${METRICS_PATH}"
fi

. /usr/local/bin/kolla_ironic_extend_start
