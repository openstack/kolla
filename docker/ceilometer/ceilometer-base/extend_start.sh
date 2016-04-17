#!/bin/bash

if [[ ! -d "/var/log/kolla/ceilometer" ]]; then
    mkdir -p /var/log/kolla/ceilometer
fi
if [[ $(stat -c %a /var/log/kolla/ceilometer) != "755" ]]; then
    chmod 755 /var/log/kolla/ceilometer
fi

source /usr/local/bin/kolla_ceilometer_extend_start
