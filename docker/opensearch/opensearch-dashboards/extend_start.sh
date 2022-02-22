#!/bin/bash

if [[ ! -d "/var/log/kolla/opensearch" ]]; then
    mkdir -p /var/log/kolla/opensearch
fi
if [[ $(stat -c %a /var/log/kolla/opensearch) != "755" ]]; then
    chmod 755 /var/log/kolla/opensearch
fi

export DASHBOARDS_HOME=/usr/share/opensearch-dashboards

PLUGIN_LIST=$($DASHBOARDS_HOME/bin/opensearch-dashboards-plugin list)
if [[ "${OPENSEARCH_DASHBOARDS_SECURITY_PLUGIN:-True}" == "False" ]]; then
    if [[ ${PLUGIN_LIST} =~ "securityDashboards" ]]; then
        $DASHBOARDS_HOME/bin/opensearch-dashboards-plugin remove securityDashboards
    fi
fi
