#!/bin/bash
set -o errexit

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    cinder-manage db sync
    exit 0
fi

if [[ "${!KOLLA_OSM[@]}" ]]; then
    if [[ "${!MAX_NUMBER[@]}" ]]; then
        cinder-manage db online_data_migrations --max_count ${MAX_NUMBER}
    else
        cinder-manage db online_data_migrations
    fi
    exit 0
fi

# Assume the service runs on top of Apache when user is root
if [[ "$(whoami)" == 'root' ]]; then
    # NOTE(pbourke): httpd will not clean up after itself in some cases which
    # results in the container not being able to restart. (bug #1489676, 1557036)
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        # Loading Apache2 ENV variables
        . /etc/apache2/envvars
        install -d /var/run/apache2/
        rm -rf /var/run/apache2/*
    else
        rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
    fi
fi
