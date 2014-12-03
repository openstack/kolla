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

# Exit unless we receive a successful response from the Glance API.
check_for_glance() {
    check_required_vars GLANCE_API_SERVICE_HOST
    GLANCE_API_URL="http://${GLANCE_API_SERVICE_HOST}:9292/"

    curl -sf -o /dev/null "$GLANCE_API_URL" || {
        echo "ERROR: glance is not available @ $GLANCE_API_URL" >&2
        exit 1
    }

    echo "glance is active @ $GLANCE_API_URL"
}

# Exit unless we receive a successful response from the Keystone API.
check_for_keystone() {
    check_required_vars KEYSTONE_PUBLIC_SERVICE_HOST

    KEYSTONE_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"

    curl -sf -o /dev/null "$KEYSTONE_URL" || {
        echo "ERROR: keystone is not available @ $KEYSTONE_URL" >&2
        exit 1
    }

    echo "keystone is active @ $KEYSTONE_URL"
}

# Exit unless we receive a successful response from the Nova API.
check_for_nova() {
    check_required_vars NOVA_API_SERVICE_HOST

    NOVA_API_URL="http://${NOVA_API_SERVICE_HOST}:8774"

    curl -sf -o /dev/null "$NOVA_API_URL" || {
        echo "ERROR: nova is not available @ $NOVA_API_URL" >&2
        exit 1
    }

    echo "nova is active @ $NOVA_API_URL"
}

# Exit unless we receive a successful response from the Neutron API.
check_for_neutron() {
    check_required_vars NEUTRON_API_SERVICE_HOST

    NEUTRON_API_URL="http://${NEUTRON_SERVER_SERVICE_HOST}:9696"

    curl -sf -o /dev/null "$NEUTRON_API_URL" || {
        echo "ERROR: neutron is not available @ $NEUTRON_API_URL" >&2
        exit 1
    }

    echo "neutron is active @ $NEUTRON_API_URL"
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

