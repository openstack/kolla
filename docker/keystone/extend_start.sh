#!/bin/bash

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. (bug #1489676, 1557036)
if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
    rm -rf /var/run/apache2/*
    APACHE_DIR="apache2"
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
    APACHE_DIR="httpd"
fi

# Create log dir for Keystone logs
KEYSTONE_LOG_DIR="/var/log/kolla/keystone"
if [[ ! -d "${KEYSTONE_LOG_DIR}" ]]; then
    mkdir -p ${KEYSTONE_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${KEYSTONE_LOG_DIR}) != "keystone:kolla" ]]; then
    chown keystone:kolla ${KEYSTONE_LOG_DIR}
fi
if [[ $(stat -c %a ${KEYSTONE_LOG_DIR}) != "755" ]]; then
    chmod 755 ${KEYSTONE_LOG_DIR}
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo -H -u keystone keystone-manage db_sync
    exit 0
fi

ARGS="-DFOREGROUND"
