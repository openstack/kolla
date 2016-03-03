#!/bin/bash

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

function get_token {
    unset OS_TOKEN OS_URL
    OS_TOKEN=$(openstack --os-identity-api-version 3 --os-username "${USERNAME}" --os-password "${PASSWORD}" --os-project-name "${PROJECT}" --os-auth-url "${ADMIN_URL}" token issue 2>&1 | awk '/ id / {print $4}')
    OS_URL="${ADMIN_URL}"
}

function fail_json {
    echo '{"failed": true, "msg": "'$1'", "changed": true}'
    exit 1
}

function exit_json {
    echo '{"failed": false, "changed": '"${changed}"'}'
}

function create_service {
    if [[ ! $(openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" service list 2>&1 | awk '/identity/') ]]; then
        openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" service create identity --name keystone 2>&1 > /dev/null
        changed="true"
    fi
}

function create_endpoints {
    endpoints=$(openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" endpoint list)
    if [[ $(echo "${endpoints}" | awk '$6 == "keystone" && $4 == "'"${REGION}"'" && $12 == "admin" {print $14;exit}') != "${ADMIN_URL}" ]]; then
        openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" endpoint create --region "${REGION}" keystone admin "${ADMIN_URL}" 2>&1 > /dev/null
        changed="true"
    fi
    if [[ $(echo "${endpoints}" | awk '$6 == "keystone" && $4 == "'"${REGION}"'" && $12 == "internal" {print $14;exit}') != "${INTERNAL_URL}" ]]; then
        openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" endpoint create --region "${REGION}" keystone internal "${INTERNAL_URL}" 2>&1 > /dev/null
        changed="true"
    fi
    if [[ $(echo "${endpoints}" | awk '$6 == "keystone" && $4 == "'"${REGION}"'" && $12 == "public" {print $14;exit}') != "${PUBLIC_URL}" ]]; then
        openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" endpoint create --region "${REGION}" keystone public "${PUBLIC_URL}" 2>&1 > /dev/null
        changed="true"
    fi
}

changed="false"
get_token
if [[ ! $(openstack --os-identity-api-version 3 --os-token "${OS_TOKEN}" --os-url "${OS_URL}" user list 2>&1 | awk '/'"${USERNAME}"'/') ]]; then
    keystone_bootstrap=$(keystone-manage bootstrap --bootstrap-username "${USERNAME}" --bootstrap-password "${PASSWORD}" --bootstrap-project-name "${PROJECT}" --bootstrap-role-name "${ROLE}" 2>&1)
    if [[ $? != 0 ]]; then
        fail_json "${keystone_bootstrap}"
    fi

    changed=$(echo "${keystone_bootstrap}" | awk '
        /Domain default already exists, skipping creation./ ||
        /Project '"${PROJECT}"' already exists, skipping creation./ ||
        /User '"${USERNAME}"' already exists, skipping creation./ ||
        /Role '"${ROLE}"' exists, skipping creation./ ||
        /User '"${USERNAME}"' already has '"${ROLE}"' on '"${PROJECT}"'./ {count++}
        END {
            if (count == 5) changed="false"; else changed="true"
            print changed
        }'
    )
fi

get_token
if [[ ! "${OS_TOKEN}" ]]; then
    fail_json "Unable to issue token"
fi
create_service
create_endpoints
exit_json
