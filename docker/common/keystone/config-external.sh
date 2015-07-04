#!/bin/bash

if [[ -f /opt/kolla/keystone/wsgi-keystone.conf ]]; then
    cp /opt/kolla/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
    chown root:keystone /etc/httpd/conf.d/wsgi-keystone.conf
    chmod 0644 /etc/httpd/conf.d/wsgi-keystone.conf
fi

if [[ -f /opt/kolla/keystone/keystone.conf ]]; then
    cp /opt/kolla/keystone/keystone.conf /etc/keystone/keystone.conf
    chown keystone: /etc/keystone/keystone.conf
    chmod 0644 /etc/keystone/keystone.conf
fi
