#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    if [[ "${CEILOMETER_DATABASE_TYPE}" == "gnocchi" ]]; then
        ceilometer-upgrade
    else
        echo "Unsupported database type: ${CEILOMETER_DATABASE_TYPE}"
        exit 1
    fi
    sudo chown -R ceilometer: /var/lib/ceilometer/
    exit 0
fi

if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    . /etc/apache2/envvars
    rm -rf /var/run/apache2/*
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
fi
