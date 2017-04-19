#!/bin/bash
set -o errexit

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    cinder-manage db sync
    exit 0
fi

if [[ "${KOLLA_INSTALL_TYPE}" == "binary" ]]; then
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        # Loading Apache2 ENV variables
        . /etc/apache2/envvars
        rm -rf /var/run/apache2/*
        APACHE_DIR="apache2"
    else
        rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
        APACHE_DIR="httpd"
    fi
fi
