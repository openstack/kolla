#!/bin/bash

SERVICE="monasca-api"

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    monasca_db upgrade
    exit 0
fi

# When Apache first starts it writes out the custom log files with root
# ownership. This later prevents the Monasca API (which runs under the
# 'monasca' user) from updating them. To avoid this we create the log
# files with the required permissions here, before Apache does.
MONASCA_API_LOG_DIR="/var/log/kolla/monasca"
for LOG_TYPE in error access; do
    if [ ! -f "${MONASCA_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log" ]; then
        touch ${MONASCA_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log
    fi
    if [[ $(stat -c %U:%G ${MONASCA_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log) != "monasca:kolla" ]]; then
        chown monasca:kolla ${MONASCA_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log
    fi
done

. /usr/local/bin/kolla_httpd_setup
