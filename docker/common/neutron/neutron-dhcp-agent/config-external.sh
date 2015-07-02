#!/bin/bash
SOURCES="/opt/kolla/neutron-dhcp-agent/neutron.conf /opt/kolla/neutron-dhcp-agent/dhcp_agent.ini /opt/kolla/neutron-dhcp-agent/dnsmasq.conf"
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
