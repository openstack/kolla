#!/bin/bash
SOURCE="/opt/kolla/horizon/local_settings"
TARGET="/etc/openstack-dashboard/local_settings"
OWNER="horizon"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi

if [[ "${KOLLA_BASE_DISTRO}" == "ubuntu" || \
        "${KOLLA_BASE_DISTRO}" == "debian" ]]; then
    SOURCE="/opt/kolla/horizon/horizon.conf"
    TARGET="/etc/apache2/sites-enabled/000-default.conf"
else
    SOURCE="/opt/kolla/horizon/horizon.conf"
    TARGET="/etc/httpd/conf.d/horizon.conf"

fi

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
