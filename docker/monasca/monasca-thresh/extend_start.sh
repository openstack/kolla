#!/bin/bash

# Create log and data directories, with appropriate permissions
MONASCA_LOG_DIR="/var/log/kolla/monasca"
MONASCA_DATA_DIR="/var/lib/monasca-thresh/data"
MONASCA_WORKER_DIR="/var/lib/monasca-thresh/worker-artifacts"
if [[ ! -d "$MONASCA_LOG_DIR" ]]; then
    mkdir -p $MONASCA_LOG_DIR
fi
if [[ ! -d "$MONASCA_DATA_DIR" ]]; then
    mkdir -p $MONASCA_DATA_DIR
fi
if [[ ! -d "$MONASCA_WORKER_DIR" ]]; then
    mkdir -p $MONASCA_WORKER_DIR
fi
if [[ $(stat -c %U:%G ${MONASCA_LOG_DIR}) != "monasca:kolla" ]]; then
    chown monasca:kolla ${MONASCA_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${MONASCA_DATA_DIR}) != "monasca:kolla" ]]; then
    chown monasca:kolla ${MONASCA_DATA_DIR}
fi
if [[ $(stat -c %U:%G ${MONASCA_WORKER_DIR}) != "monasca:kolla" ]]; then
    chown monasca:kolla ${MONASCA_WORKER_DIR}
fi
if [[ $(stat -c %a ${MONASCA_LOG_DIR}) != "755" ]]; then
    chmod 755 ${MONASCA_LOG_DIR}
fi
if [[ $(stat -c %a ${MONASCA_DATA_DIR}) != "755" ]]; then
    chmod 755 ${MONASCA_DATA_DIR}
fi
if [[ $(stat -c %a ${MONASCA_WORKER_DIR}) != "755" ]]; then
    chmod 755 ${MONASCA_WORKER_DIR}
fi

# Delete the contents of data and worker-artifacts directories as
# Apache Storm doesn't clear temp files unless shutdown gracefully.
if [[ $(ls -Ab ${MONASCA_DATA_DIR}) != "" ]]; then
    find ${MONASCA_DATA_DIR} -mindepth 1 -delete
fi
if [[ $(ls -Ab ${MONASCA_WORKER_DIR}) != "" ]]; then
    find ${MONASCA_WORKER_DIR} -mindepth 1 -delete
fi

. /usr/local/bin/kolla_monasca_extend_start

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    . /usr/local/bin/topology_bootstrap
fi
