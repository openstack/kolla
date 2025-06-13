#!/bin/bash

if [[ ! -r "/var/log/kolla/openvswitch/ovn-sb-db.log" ]]; then
    touch /var/log/kolla/openvswitch/ovn-sb-db.log
    chown openvswitch:openvswitch /var/log/kolla/openvswitch/ovn-sb-db.log
fi
