#!/bin/bash

if [[ ! -r "/var/log/kolla/openvswitch/ovn-sb-relay-${RELAY_ID}.log" ]]; then
    touch /var/log/kolla/openvswitch/ovn-sb-relay-${RELAY_ID}.log
    chown openvswitch:openvswitch /var/log/kolla/openvswitch/ovn-sb-relay-${RELAY_ID}.log
fi
