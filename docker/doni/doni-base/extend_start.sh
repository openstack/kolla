#!/bin/bash

LOG_PATH=/var/log/kolla/doni

if [[ ! -d "${LOG_PATH}" ]]; then
    mkdir -p "${LOG_PATH}"
fi
if [[ $(stat -c %a "${LOG_PATH}") != "755" ]]; then
    chmod 755 "${LOG_PATH}"
fi

. /usr/local/bin/kolla_doni_extend_start
