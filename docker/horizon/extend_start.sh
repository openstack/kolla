#!/bin/bash

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. (bug #1489676, 1557036)
if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    source /etc/apache2/envvars
    rm -rf /var/run/apache2/*
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
fi

# NOTE(jeffrey4l): The local_settings file affect django-compress
# behavior, so re-generate the compressed javascript and css if it
# is changed
MD5SUM_TXT_PATH="/tmp/.local_settings.md5sum.txt"
if [[ ! -f ${MD5SUM_TXT_PATH} || $(md5sum -c --status ${MD5SUM_TXT_PATH};echo $?) != 0 ]]; then
    md5sum /etc/openstack-dashboard/local_settings > ${MD5SUM_TXT_PATH}
    if [[ "${KOLLA_INSTALL_TYPE}" == "binary" ]]; then
        /usr/bin/manage.py compress --force
    elif [[ "${KOLLA_INSTALL_TYPE}" == "source" ]]; then
        /var/lib/kolla/venv/bin/python /var/lib/kolla/venv/bin/manage.py compress --force
    fi
fi

# NOTE(sbezverk) since Horizon is now storing logs in its own location, /var/log/horizon
# needs to be created if it does not exist
if [[ ! -d "/var/log/kolla/horizon" ]]; then
    mkdir -p /var/log/kolla/horizon
fi
if [[ $(stat -c %a /var/log/kolla/horizon) != "755" ]]; then
    chmod 755 /var/log/kolla/horizon
fi
