#!/bin/bash

KIBANA_LOG_DIR="/var/log/kolla/kibana"
KIBANA_DEFAULT_EXECUTABLE="/opt/kibana/bin/kibana"

# (niedbalski): debian installs under /usr/share, so lets create
# a symlink to the common executable location see LP #1772750.
if [[ ! -e ${KIBANA_DEFAULT_EXECUTABLE} ]] && [[ -f /usr/share/kibana/bin/kibana ]]; then
    mkdir -p $(dirname ${KIBANA_DEFAULT_EXECUTABLE}) && ln -s /usr/share/kibana/bin/kibana ${KIBANA_DEFAULT_EXECUTABLE}
fi

if [[ ! -d "${KIBANA_LOG_DIR}" ]]; then
    mkdir -p "${KIBANA_LOG_DIR}"
fi
if [[ $(stat -c %U:%G "${KIBANA_LOG_DIR}") != "kibana:kolla" ]]; then
    chown kibana:kolla "${KIBANA_LOG_DIR}"
fi
