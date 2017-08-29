#!/bin/bash

if [[ ! -d "/var/log/kolla/almanach" ]]; then
    mkdir -p /var/log/kolla/almanach
fi
if [[ $(stat -c %a /var/log/kolla/almanach) != "755" ]]; then
    chmod 755 /var/log/kolla/almanach
fi
