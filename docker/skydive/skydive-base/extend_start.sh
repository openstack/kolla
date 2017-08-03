#!/bin/bash

if [[ ! -d "/var/log/kolla/skydive" ]]; then
    mkdir -p /var/log/kolla/skydive
fi
if [[ $(stat -c %a /var/log/kolla/skydive) != "755" ]]; then
    chmod 755 /var/log/kolla/skydive
fi
