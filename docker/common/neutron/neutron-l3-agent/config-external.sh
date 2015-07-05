#!/bin/bash
SOURCES="/opt/kolla/neutron-l3-agent/neutron.conf /opt/kolla/neutron-l3-agent/l3_agent.ini /opt/kolla/neutron-l3-agent/fwaas_driver.ini"
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
