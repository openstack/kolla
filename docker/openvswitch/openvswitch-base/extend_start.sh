#!/bin/bash

if [[ ! -d "/var/log/kolla/openvswitch" ]]; then
    mkdir -p /var/log/kolla/openvswitch
fi
if [[ $(stat -c %a /var/log/kolla/openvswitch) != "755" ]]; then
    chmod 755 /var/log/kolla/openvswitch
fi

. /usr/local/bin/kolla_openvswitch_extend_start
