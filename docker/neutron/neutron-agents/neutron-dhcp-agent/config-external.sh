#!/bin/bash
SOURCES="/opt/kolla/neutron-agents/neutron.conf /opt/kolla/neutron-agents/dhcp_agent.ini /opt/kolla/neutron-agents/dnsmasq.conf"
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
