#!/bin/bash

# Create log directory, with appropriate permissions
INFLUXDB_LOG_DIR=/var/log/kolla/influxdb

if [[ ! -d "${INFLUXDB_LOG_DIR}" ]]; then
    mkdir -p ${INFLUXDB_LOG_DIR}
fi
if [[ $(stat -c %a ${INFLUXDB_LOG_DIR}) != "755" ]]; then
    chmod 755 ${INFLUXDB_LOG_DIR}
fi
