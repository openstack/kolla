#!/bin/bash

mkdir -p "/run/openvswitch"
if [[ ! -e "/var/lib/openvswitch/ovnnb.db" ]]; then
    ovsdb-tool create "/var/lib/openvswitch/ovnnb.db" "/usr/share/openvswitch/ovn-nb.ovsschema"
fi
