#!/bin/bash

mkdir -p "/run/openvswitch"
if [[ ! -e "/var/lib/openvswitch/conf.db" ]]; then
    ovsdb-tool create "/var/lib/openvswitch/conf.db"
fi
