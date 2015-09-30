#!/bin/bash

mkdir -p "/run/openvswitch"
if [[ ! -e "/etc/openvswitch/conf.db" ]]; then
    ovsdb-tool create "/etc/openvswitch/conf.db"
fi
