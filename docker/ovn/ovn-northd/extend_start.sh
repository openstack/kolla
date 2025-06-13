#!/bin/bash
if [[ ! -r "/var/log/kolla/openvswitch/ovn-northd.log" ]]; then
    touch /var/log/kolla/openvswitch/ovn-northd.log
    chown openvswitch:openvswitch /var/log/kolla/openvswitch/ovn-northd.log
fi
