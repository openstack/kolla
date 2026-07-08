#!/bin/bash

if [[ ! -d "/var/log/kolla/skyline" ]]; then
    mkdir -p /var/log/kolla/skyline
fi
if [[ $(stat -c %U:%G /var/log/kolla/skyline) != "skyline:kolla" ]]; then
    chown skyline:kolla /var/log/kolla/skyline
fi
if [[ $(stat -c %a /var/log/kolla/skyline) != "755" ]]; then
    chmod 755 /var/log/kolla/skyline
fi

if [[ ! -d "/var/lib/skyline" ]]; then
    mkdir -p /var/lib/skyline
fi
if [[ $(stat -c %U:%G /var/lib/skyline) != "skyline:kolla" ]]; then
    chown skyline:kolla /var/lib/skyline
fi
if [[ $(stat -c %a /var/lib/skyline) != "755" ]]; then
    chmod 755 /var/lib/skyline
fi

. /usr/local/bin/kolla_skyline_extend_start
