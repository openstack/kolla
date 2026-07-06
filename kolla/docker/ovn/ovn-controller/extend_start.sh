#!/bin/bash

if [[ ! -r "/var/log/kolla/openvswitch/ovn-controller.log" ]]; then
    touch /var/log/kolla/openvswitch/ovn-controller.log
    chown openvswitch:openvswitch /var/log/kolla/openvswitch/ovn-controller.log
fi
