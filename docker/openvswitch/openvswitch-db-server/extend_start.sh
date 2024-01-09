#!/bin/bash

mkdir -p "/run/openvswitch"
if [[ ! -e "/var/lib/openvswitch/conf.db" ]]; then
    ovsdb-tool create "/var/lib/openvswitch/conf.db"
fi

if [[ $(ovsdb-tool needs-conversion /var/lib/openvswitch/conf.db) == yes ]]; then
    ovsdb-tool convert "/var/lib/openvswitch/conf.db"
fi
