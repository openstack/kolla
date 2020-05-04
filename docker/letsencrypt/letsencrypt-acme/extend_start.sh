#!/bin/bash

LETSENCRYPT_LOG_DIR="/var/log/kolla/letsencrypt"

if [[ ! -d "${LETSENCRYPT_LOG_DIR}" ]]; then
    mkdir -p "${LETSENCRYPT_LOG_DIR}"
fi
if [[ $(stat -c %U:%G "${LETSENCRYPT_LOG_DIR}") != "letsencrypt:kolla" ]]; then
    chown letsencrypt:kolla "${LETSENCRYPT_LOG_DIR}"
fi
