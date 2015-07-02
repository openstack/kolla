#!/bin/bash
SOURCES="/opt/kolla/neutron-metadata-agent/neutron.conf /opt/kolla/neutron-metadata-agent/metadata_agent.ini"
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
