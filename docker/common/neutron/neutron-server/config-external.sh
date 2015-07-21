#!/bin/bash
SOURCE="/opt/kolla/neutron-server/neutron.conf"
TARGET="/etc/neutron/neutron.conf"
OWNER="neutron"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi

# TODO(SamYaple): Remove this from neutron-server once bootstrap is understood
SOURCE="/opt/kolla/neutron-openvswitch-agent/ml2_conf.ini"
TARGET="/etc/neutron/plugins/ml2/ml2_conf.ini"
OWNER="neutron"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
