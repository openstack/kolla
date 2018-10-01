#!/bin/bash

# Create log directory, with appropriate permissions
MONASCA_LOG_DIR="/var/log/kolla/monasca"
if [[ ! -d "$MONASCA_LOG_DIR" ]]; then
    mkdir -p $MONASCA_LOG_DIR
fi
if [[ $(stat -c %U:%G ${MONASCA_LOG_DIR}) != "monasca:kolla" ]]; then
    chown monasca:kolla ${MONASCA_LOG_DIR}
fi
if [[ $(stat -c %a ${MONASCA_LOG_DIR}) != "755" ]]; then
    chmod 755 ${MONASCA_LOG_DIR}
fi

. /usr/local/bin/kolla_monasca_extend_start
