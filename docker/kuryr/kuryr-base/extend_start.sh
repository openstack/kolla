#!/bin/bash

KURYR_LOG_DIR=/var/log/kolla/kuryr

if [[ ! -d "${KURYR_LOG_DIR}" ]]; then
    mkdir -p ${KURYR_LOG_DIR}
fi
if [[ $(stat -c %a ${KURYR_LOG_DIR}) != "755" ]]; then
    chmod 755 ${KURYR_LOG_DIR}
fi

if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    mkdir -p /usr/lib/docker/plugins/kuryr
    exit 0
fi
