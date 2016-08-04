#!/bin/bash

set -x

# NOTE(SamYaple): Kolla needs to wraps `keystone-manage bootstrap` to ensure
# any change is reported correctly for idempotency. This script will exit with
# valid json that can be parsed with information about if the task has failed
# and if anything changed.

USERNAME=$1
PASSWORD=$2
PROJECT=$3
ROLE=$4
ADMIN_URL=$5
INTERNAL_URL=$6
PUBLIC_URL=$7
REGION=$8

function fail_json {
    echo '{"failed": true, "msg": "'$1'", "changed": true}'
    exit 1
}

function exit_json {
    echo '{"failed": false, "changed": '"${changed}"'}'
}

function kolla_kubernetes {
    KUBE_TOKEN=$(</var/run/secrets/kubernetes.io/serviceaccount/token)
    bootstrap_url=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCPORT/api/v1/namespaces/default/pods | grep /api/v1/namespaces/default/pods/keystone-bootstrap | cut -d '"' -f 4) || true
    KEYSTONE_BOOTSTRAPPED=$(curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCPORT$bootstrap_url | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["status"]["phase"]') || KEYSTONE_BOOTSTRAPPED='Succeeded'

    if [[ "$KEYSTONE_BOOTSTRAPPED" != "Succeeded" ]]; then
        echo "Keystone bootstrapping isn't complete"
        exit 1
    fi
}

#***** KOLLA-KUBERNETES *****
# TODO: Add a kolla_kubernetes script at build time when templating is complete
if [[ "${!KOLLA_KUBERNETES[@]}" ]]; then
    kolla_kubernetes
fi
#***** KOLLA-KUBERNETES *****

changed="false"
keystone_bootstrap=$(keystone-manage bootstrap --bootstrap-username "${USERNAME}" --bootstrap-password "${PASSWORD}" --bootstrap-project-name "${PROJECT}" --bootstrap-role-name "${ROLE}" --bootstrap-admin-url "${ADMIN_URL}" --bootstrap-internal-url "${INTERNAL_URL}" --bootstrap-public-url "${PUBLIC_URL}" --bootstrap-service-name "keystone" --bootstrap-region-id "${REGION}" 2>&1)
if [[ $? != 0 ]]; then
    fail_json "${keystone_bootstrap}"
fi

changed=$(echo "${keystone_bootstrap}" | awk '
    /Domain default already exists, skipping creation./ ||
    /Project '"${PROJECT}"' already exists, skipping creation./ ||
    /User '"${USERNAME}"' already exists, skipping creation./ ||
    /Role '"${ROLE}"' exists, skipping creation./ ||
    /User '"${USERNAME}"' already has '"${ROLE}"' on '"${PROJECT}"'./ ||
    /Region '"${REGION}"' exists, skipping creation./ ||
    /Skipping admin endpoint as already created/ ||
    /Skipping internal endpoint as already created/ ||
    /Skipping public endpoint as already created/ {count++}
    END {
        if (count == 9) changed="false"; else changed="true"
        print changed
    }'
)

exit_json
