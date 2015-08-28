#!/bin/bash
SOURCES="/opt/kolla/neutron-agents/neutron.conf /opt/kolla/neutron-agents/l3_agent.ini /opt/kolla/neutron-agents/fwaas_driver.ini"
TARGET="/etc/neutron/"
OWNER="neutron"

for f in $SOURCES; do
    if [[ -f "$f" ]]; then
        fname=$(basename $f)
        cp $f $TARGET
        chown ${OWNER}: $TARGET/$fname
        chmod 0644 $TARGET/$fname
    fi
done

SOURCE="/opt/kolla/neutron-agents/ml2_conf.ini"
TARGET="/etc/neutron/plugins/ml2/ml2_conf.ini"
OWNER="neutron"

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
