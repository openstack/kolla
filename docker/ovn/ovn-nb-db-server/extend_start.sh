#!/bin/bash

mkdir -p "/run/openvswitch"

# Check for the presence of schema file in the old
# location before accessing it.
# Note: If latest OVN is used (post split from openvswitch),
# then the new location for the schema file
# is - /usr/share/ovn/ovn-nb.ovsschema.
# It is advisable to use the ovn-ctl script to start
# ovn NB db server. ovn-ctl takes care of creating the
# db file from the schema file if the db file is not
# present. ovn-ctl also takes care of updating the db file
# if the schema file is updated.
if [[ -e "/usr/share/openvswitch/ovn-nb.ovsschema" ]]; then
    if [[ ! -e "/var/lib/openvswitch/ovnnb.db" ]]; then
        ovsdb-tool create "/var/lib/openvswitch/ovnnb.db" "/usr/share/openvswitch/ovn-nb.ovsschema"
    fi
fi
