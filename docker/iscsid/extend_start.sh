#!/bin/bash

# check if unique iSCSI initiator name already exists
if [[ ! -f /etc/iscsi/initiatorname.iscsi ]]; then
    echo "Generating new iSCSI initiator name"
    echo InitiatorName=$(/sbin/iscsi-iname) > /etc/iscsi/initiatorname.iscsi
fi
