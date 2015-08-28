#!/bin/bash
SOURCE="/opt/kolla/neutron-openvswitch-agent/neutron.conf"
TARGET="/etc/neutron/neutron.conf"
OWNER="neutron"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi

SOURCE="/opt/kolla/neutron-openvswitch-agent/ml2_conf.ini"
TARGET="/etc/neutron/plugins/ml2/ml2_conf.ini"
OWNER="neutron"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
