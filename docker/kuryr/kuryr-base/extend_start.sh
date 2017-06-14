#!/bin/bash

KURYR_LOG_DIR=/var/log/kolla/kuryr
KURYR_DOCKER_PLUGINS_DIR=/usr/lib/docker/plugins/kuryr

if [[ ! -d "${KURYR_LOG_DIR}" ]]; then
    mkdir -p ${KURYR_LOG_DIR}
fi
if [[ $(stat -c %a ${KURYR_LOG_DIR}) != "755" ]]; then
    chmod 755 ${KURYR_LOG_DIR}
fi

if [[ ! -d "${KURYR_DOCKER_PLUGINS_DIR}" ]]; then
    mkdir -p ${KURYR_DOCKER_PLUGINS_DIR}
fi
