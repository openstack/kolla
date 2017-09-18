#!/bin/bash

OPENDAYLIGHT_LOG_DIR=/var/log/kolla/opendaylight

if [[ ! -d "${OPENDAYLIGHT_LOG_DIR}" ]]; then
    mkdir -p "${OPENDAYLIGHT_LOG_DIR}"
fi
if [[ $(stat -c %a "${OPENDAYLIGHT_LOG_DIR}") != "755" ]]; then
    chmod 755 "${OPENDAYLIGHT_LOG_DIR}"
fi

# start ODL for source install
if [[ ${KOLLA_INSTALL_TYPE} == "source" ]]; then
    /karaf-*-SNAPSHOT/bin/start
fi
