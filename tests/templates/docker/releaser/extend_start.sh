#!/bin/bash

if [[ ! -d "/var/log/kolla/releaser" ]]; then
    mkdir -p /var/log/kolla/releaser
fi

if [[ $(stat -c %a /var/log/kolla/releaser) != "755" ]]; then
    chmod 755 /var/log/kolla/releaser
fi

. /usr/local/bin/kolla_releaser_extend_start
