#!/bin/bash

. /opt/kolla/service_hosts.sh

# Set some generally useful defaults.
MY_IP=$(ip route get $(ip route | awk '$1 == "default" {print $3}') |
    awk '$4 == "src" {print $5}')

: ${PUBLIC_IP:=${MY_IP}}

# Iterate over a list of variable names and exit if one is
# undefined.
check_required_vars() {
    for var in $*; do
        if [ -z "${!var}" ]; then
            echo "ERROR: missing $var" >&2
            exit 1
        fi
    done
}

# Exit unless we receive a successful response from corresponding OpenStack
# service.
check_for_os_service() {
    local name=$1
    local host_var=$2
    local port=$3
    local api_version=$4

    check_required_vars $host_var

    local endpoint="http://${!host_var}:$port/$api_version"

    curl -sf -o /dev/null "$endpoint" || {
        echo "ERROR: $name is not available @ $endpoint" >&2
        exit 1
    }

    echo "$name is active @ $endpoint"
}

check_for_glance() {
    check_for_os_service glance GLANCE_API_SERVICE_HOST 9292
}

check_for_keystone() {
    check_for_os_service keystone KEYSTONE_PUBLIC_SERVICE_HOST 5000 v2.0
}

check_for_nova() {
    check_for_os_service nova NOVA_API_SERVICE_HOST 8774
}

check_for_neutron() {
    check_for_os_service neutron NEUTRON_SERVER_SERVICE_HOST 9696
}

# Exit unless we receive a successful response from the database server.
check_for_db() {
    check_required_vars MARIADB_SERVICE_HOST DB_ROOT_PASSWORD

    mysql -h ${MARIADB_SERVICE_HOST} -u root -p"${DB_ROOT_PASSWORD}" \
            -e "select 1" mysql > /dev/null 2>&1 || {
        echo "ERROR: database is not available @ $MARIADB_SERVICE_HOST" >&2
        exit 1
    }

    echo "database is active @ ${MARIADB_SERVICE_HOST}"
}

# Dump shell environment to a file
dump_vars() {
    set -o posix
    set > /pid_$$_vars.sh
    set +o posix
}

