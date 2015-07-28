#!/bin/bash

set -o errexit

check_required_vars OVS_DB_FILE \
                    OVS_UNIXSOCK


mkdir -p "$(dirname $OVS_UNIXSOCK)"

if [[ ! -e "${OVS_DB_FILE}" ]]; then
    ovsdb-tool create "${OVS_DB_FILE}"
fi

exec ovsdb-server $OVS_DB_FILE -vconsole:emer -vsyslog:err -vfile:info --remote=punix:"${OVS_UNIXSOCK}" --log-file="${OVS_LOG_FILE}"
