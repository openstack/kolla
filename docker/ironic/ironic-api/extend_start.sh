#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    ironic-dbsync upgrade
    ironic-dbsync online_data_migrations
    exit 0
fi

if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    ironic-dbsync upgrade
    exit 0
fi

if [[ "${!KOLLA_OSM[@]}" ]]; then
    ironic-dbsync online_data_migrations
    exit 0
fi

# Assume the service runs on top of Apache when user is root
if [[ "$(whoami)" == 'root' ]]; then
    # NOTE(pbourke): httpd will not clean up after itself in some cases which
    # results in the container not being able to restart. (bug #1489676, 1557036)
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        # Loading Apache2 ENV variables
        . /etc/apache2/envvars
        rm -rf /var/run/apache2/*
    else
        rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
    fi
fi
