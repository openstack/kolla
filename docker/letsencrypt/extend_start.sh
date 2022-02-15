#!/bin/bash

if [[ ! -d "/var/log/kolla/letsencrypt" ]]; then
    mkdir -p /var/log/kolla/letsencrypt
fi
if [[ $(stat -c %a /var/log/kolla/letsencrypt) != "755" ]]; then
    chmod 755 /var/log/kolla/letsencrypt
fi

. /usr/local/bin/kolla_httpd_setup
