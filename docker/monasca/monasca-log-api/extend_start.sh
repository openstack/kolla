#!/bin/bash

SERVICE="monasca-log-api"

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. (bug #1489676, 1557036)
if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    . /etc/apache2/envvars
    rm -rf /var/run/apache2/*
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
fi

# When Apache first starts it writes out the custom log files with root
# ownership. This later prevents the Monasca Log API (which runs under the
# 'monasca' user) from updating them. To avoid this we create the log
# files with the required permissions here, before Apache does.
MONASCA_LOG_API_LOG_DIR="/var/log/kolla/monasca"
for LOG_TYPE in error access; do
    if [ ! -f "${MONASCA_LOG_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log" ]; then
        touch ${MONASCA_LOG_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log
    fi
    if [[ $(stat -c %U:%G ${MONASCA_LOG_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log) != "monasca:kolla" ]]; then
        chown monasca:kolla ${MONASCA_LOG_API_LOG_DIR}/${SERVICE}-${LOG_TYPE}.log
    fi
done
