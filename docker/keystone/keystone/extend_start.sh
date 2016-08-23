#!/bin/bash

function kolla_kubernetes {
    KUBE_TOKEN=$(</var/run/secrets/kubernetes.io/serviceaccount/token)
    bootstrap_url=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCPORT/api/v1/namespaces/default/pods | grep /api/v1/namespaces/default/pods/keystone-bootstrap | cut -d '"' -f 4) || true
    KEYSTONE_BOOTSTRAPPED=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCPORT$bootstrap_url | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["status"]["phase"]') || KEYSTONE_BOOTSTRAPPED='Succeeded'

    if [[ "$KEYSTONE_BOOTSTRAPPED" != "Succeeded" ]]; then
        echo "Keystone bootstrapping isn't complete"
        exit 1
    fi
}

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. (bug #1489676, 1557036)
if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    . /etc/apache2/envvars
    rm -rf /var/run/apache2/*
    APACHE_DIR="apache2"
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
    APACHE_DIR="httpd"
fi

# Create log dir for Keystone logs
KEYSTONE_LOG_DIR="/var/log/kolla/keystone"
if [[ ! -d "${KEYSTONE_LOG_DIR}" ]]; then
    mkdir -p ${KEYSTONE_LOG_DIR}
fi
if [[ $(stat -c %U:%G ${KEYSTONE_LOG_DIR}) != "keystone:kolla" ]]; then
    chown keystone:kolla ${KEYSTONE_LOG_DIR}
fi
if [[ $(stat -c %a ${KEYSTONE_LOG_DIR}) != "755" ]]; then
    chmod 755 ${KEYSTONE_LOG_DIR}
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo -H -u keystone keystone-manage db_sync
    exit 0
fi

ARGS="-DFOREGROUND"

#***** KOLLA-KUBERNETES *****
# TODO: Add a kolla_kubernetes script at build time when templating is complete
if [[ "${!KOLLA_KUBERNETES[@]}" ]]; then
    kolla_kubernetes
fi
#***** KOLLA-KUBERNETES *****
