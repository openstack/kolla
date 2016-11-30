#!/bin/bash

set -o errexit

OCTAVIA_LOG_DIR=/var/log/kolla/octavia

if [[ ! -d "${OCTAVIA_LOG_DIR}" ]]; then
    mkdir -p ${OCTAVIA_LOG_DIR}
fi
if [[ $(stat -c %a ${OCTAVIA_LOG_DIR}) != "755" ]]; then
    chmod 755 ${OCTAVIA_LOG_DIR}
fi

. /usr/local/bin/kolla_octavia_extend_start
