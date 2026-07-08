#!/bin/bash

# Logs

if [[ ! -d "/var/log/kolla/letsencrypt" ]]; then
    mkdir -p /var/log/kolla/letsencrypt
fi
if [[ $(stat -c %a /var/log/kolla/letsencrypt) != "755" ]]; then
    chmod 755 /var/log/kolla/letsencrypt
fi

# Structure for lego and webserver

FOLDERS_LEGO="/etc/letsencrypt /etc/letsencrypt/lego /etc/letsencrypt/lego/internal /etc/letsencrypt/lego/external"
FOLDERS_WEBSERVER="/etc/letsencrypt/http-01 /etc/letsencrypt/http-01/.well-known /etc/letsencrypt/http-01/.well-known/acme-challenge"

if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    USER="www-data"
    GROUP="www-data"
    USERGROUP_WEBSERVER="${USER}:${GROUP}"
    USERGROUP="haproxy:haproxy"
else
    USER="apache"
    GROUP="apache"
    USERGROUP_WEBSERVER="${USER}:${GROUP}"
    USERGROUP="haproxy:haproxy"
fi

for folder in ${FOLDERS_LEGO}; do
    if [[ ! -d "${folder}" ]]; then
        mkdir -p ${folder}
    fi

    if [[ $(stat -c %U:%G ${folder}) != "${USERGROUP}" ]]; then
        if getent passwd ${USER} 2 > /dev/null; then
            chown ${USERGROUP} ${folder}
        fi
    fi

    if [[ "${folder}" == "/etc/letsencrypt" ]]; then
        if [[ $(stat -c %a ${folder}) != "751" ]]; then
            chmod 751 ${folder}
        fi
    else
        if [[ $(stat -c %a ${folder}) != "755" ]]; then
            chmod 755 ${folder}
        fi
    fi
done

for folder in ${FOLDERS_WEBSERVER}; do
    if [[ ! -d "${folder}" ]]; then
        mkdir -p ${folder}
    fi

    if [[ $(stat -c %U:%G ${folder}) != "${USERGROUP_WEBSERVER}" ]]; then
        if getent passwd ${USER} 2 > /dev/null; then
            chown ${USERGROUP_WEBSERVER} ${folder}
        fi
    fi

    if [[ $(stat -c %a ${folder}) != "755" ]]; then
        chmod 755 ${folder}
    fi
done

if [ -e /usr/local/bin/kolla_letsencrypt_extend_start ]; then
    . /usr/local/bin/kolla_letsencrypt_extend_start
fi
