#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    if [[ "${CEILOMETER_DATABASE_TYPE}" == "mysql" ]]; then
        sudo -H -u ceilometer ceilometer-upgrade --skip-gnocchi-resource-types
    elif [[ "${CEILOMETER_DATABASE_TYPE}" == "gnocchi" ]]; then
        sudo -H -u ceilometer ceilometer-upgrade --skip-metering-database
    elif [[ "${CEILOMETER_DATABASE_TYPE}" == "mongodb" ]]; then
        echo "Ceilometer doesn't need to initialize a database when MongoDB is configured as the database back end."
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
