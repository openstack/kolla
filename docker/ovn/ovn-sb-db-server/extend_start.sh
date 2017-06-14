#!/bin/bash

mkdir -p "/run/openvswitch"
if [[ ! -e "/var/lib/openvswitch/ovnsb.db" ]]; then
    ovsdb-tool create "/var/lib/openvswitch/ovnsb.db" "/usr/share/openvswitch/ovn-sb.ovsschema"
fi
