#!/bin/bash

CEILOMETER_LOG_DIR=/var/log/kolla/ceilometer

if [[ ! -d "${CEILOMETER_LOG_DIR}" ]]; then
    mkdir -p "${CEILOMETER_LOG_DIR}"
fi
if [[ $(stat -c %U:%G "${CEILOMETER_LOG_DIR}") != "ceilometer:kolla" ]]; then
    chown ceilometer:kolla "${CEILOMETER_LOG_DIR}"
fi
if [[ $(stat -c %a "${CEILOMETER_LOG_DIR}") != "755" ]]; then
    chmod 755 "${CEILOMETER_LOG_DIR}"
fi

. /usr/local/bin/kolla_ceilometer_extend_start
