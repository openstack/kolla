#!/bin/bash
if [[ ! -d "/var/log/kolla/openvswitch/netcontrold" ]]; then
    mkdir -p /var/log/kolla/openvswitch/netcontrold
fi
if [[ $(stat -c %a /var/log/kolla/openvswitch/netcontrold) != "755" ]]; then
    chmod 755 /var/log/kolla/openvswitch/netcontrold
fi
