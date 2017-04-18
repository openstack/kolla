#!/bin/bash

LOG_PATH=/var/log/kolla/ironic-inspector

if [[ ! -d "${LOG_PATH}" ]]; then
    mkdir -p "${LOG_PATH}"
fi
if [[ $(stat -c %a "${LOG_PATH}") != "755" ]]; then
    chmod 755 "${LOG_PATH}"
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    ironic-inspector-dbsync --config-file /etc/ironic-inspector/inspector.conf upgrade
    exit 0
fi
