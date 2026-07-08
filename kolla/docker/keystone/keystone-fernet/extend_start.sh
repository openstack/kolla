#!/bin/bash

FERNET_SYNC=/usr/bin/fernet-node-sync.sh
FERNET_TOKEN_DIR="/etc/keystone/fernet-keys"

if [[ -f "${FERNET_SYNC}" ]]; then
    ${FERNET_SYNC}
fi

if [[ $(stat -c %U:%G ${FERNET_TOKEN_DIR}) != "keystone:keystone" ]]; then
    chown keystone:keystone ${FERNET_TOKEN_DIR}
fi
