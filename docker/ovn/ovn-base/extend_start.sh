#!/bin/bash

if [[ ! -d "/run/ovn" ]]; then
    mkdir -p /run/ovn
fi
if [[ ! -d "/var/log/kolla/openvswitch" ]]; then
    mkdir -p /var/log/kolla/openvswitch
fi
if [[ $(stat -c %a /var/log/kolla/openvswitch) != "755" ]]; then
    chmod 755 /var/log/kolla/openvswitch
fi

. /usr/local/bin/kolla_ovn_extend_start
