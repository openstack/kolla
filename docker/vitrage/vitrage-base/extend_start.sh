#!/bin/bash

VITRAGE_LOG_DIR="/var/log/kolla/vitrage"
if [[ ! -d "${VITRAGE_LOG_DIR}" ]]; then
    mkdir -p ${VITRAGE_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${VITRAGE_LOG_DIR}) != "vitrage:kolla" ]]; then
    chown vitrage:kolla ${VITRAGE_LOG_DIR}
fi
if [[ $(stat -c %a ${VITRAGE_LOG_DIR}) != "755" ]]; then
    chmod 755 ${VITRAGE_LOG_DIR}
fi
