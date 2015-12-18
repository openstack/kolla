#!/bin/bash

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
fi

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. Unconfirmed if this
# happens on Ubuntu. (bug #1489676)
if [[ "${KOLLA_BASE_DISTRO}" =~ fedora|centos|oraclelinux|rhel ]]; then
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo -H -u keystone keystone-manage db_sync
    exit 0
fi

ARGS="-DFOREGROUND"
