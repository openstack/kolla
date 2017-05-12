#!/bin/bash

if [[ ! -d "/var/log/kolla/zaqar" ]]; then
    mkdir -p /var/log/kolla/zaqar
fi
if [[ $(stat -c %a /var/log/kolla/zaqar) != "755" ]]; then
    chmod 755 /var/log/kolla/zaqar
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
