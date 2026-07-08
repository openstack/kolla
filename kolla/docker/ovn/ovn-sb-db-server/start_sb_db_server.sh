#!/bin/bash

# All the option passed to this script will be
# passed to the ovn-ctl script. Please see the options
# supported by ovn-ctl script -
# https://github.com/ovn-org/ovn/blob/master/utilities/ovn-ctl
args=$@

# Use ovn-ctl script to start ovn SB db server as it
# takes care of creating the db file from the schema
# file if the db file is not present. It also takes care
# of updating the db file if the schema file is updated.

# Check for the presence of ovn-ctl script in two locations.
# If latest OVN is used (post split from openvswitch),
# then the new location for the ovn-ctl script is
# is - /usr/share/ovn/scripts/ovn-ctl. Otherwise it is
# /usr/share/openvswitch/scripts/ovn-ctl.


if [[ -f "/usr/share/openvswitch/scripts/ovn-ctl" ]]; then
    set /usr/share/openvswitch/scripts/ovn-ctl --no-monitor
elif [[  -f "/usr/share/ovn/scripts/ovn-ctl" ]]; then
    set /usr/share/ovn/scripts/ovn-ctl --no-monitor
else
    exit 1
fi

$@ $args run_sb_ovsdb
