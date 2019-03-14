#!/bin/bash

# Create log directory, with appropriate permissions
CASO_LOG_DIR="/var/log/kolla/caso"
if [[ ! -d "$CASO_LOG_DIR" ]]; then
    mkdir -p $CASO_LOG_DIR
fi
if [[ $(stat -c %U:%G ${CASO_LOG_DIR}) != "caso:kolla" ]]; then
    chown caso:kolla ${CASO_LOG_DIR}
fi
if [[ $(stat -c %a ${CASO_LOG_DIR}) != "755" ]]; then
    chmod 755 ${CASO_LOG_DIR}
fi

. /usr/local/bin/kolla_caso_extend_start
