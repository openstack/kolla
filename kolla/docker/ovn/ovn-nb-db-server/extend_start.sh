#!/bin/bash

if [[ ! -r "/var/log/kolla/openvswitch/ovn-nb-db.log" ]]; then
    touch /var/log/kolla/openvswitch/ovn-nb-db.log
    chown openvswitch:openvswitch /var/log/kolla/openvswitch/ovn-nb-db.log
fi
