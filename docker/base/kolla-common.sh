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

# The usage of the wait_for function looks like the following
#     wait_for LOOPS_NUMBER SLEEP_TIME ARGS
#
# The ARGS are read and concatenated together into a single command and the
# command is executed in a loop until it succeeds or reaches the max number of
# attempts (LOOPS_NUMBER).
#
# Optional variables SUCCESSFUL_MATCH_OUTPUT and FAIL_MATCH_OUTPUT variable may
# also be set to control if the loop exits early if the commands stdout/stderr
# matches the supplied regex string. Consider using the `wait_for_output` and
# `wait_for_output_unless` functions in case there is a need to check for the
# command output.
#
# The script exits on failure, either when output contains string identified as
# failure, or when it reaches a timeout.
#
# Examples:
#     wait_for 30 10 ping -c 1 192.0.2.2
#     wait_for 10 1 ls file_we_are_waiting_for
#     wait_for 10 3 date \| grep 8
wait_for() {
    local loops=${1:-""}
    local sleeptime=${2:-""}
    FAIL_MATCH_OUTPUT=${FAIL_MATCH_OUTPUT:-""}
    SUCCESSFUL_MATCH_OUTPUT=${SUCCESSFUL_MATCH_OUTPUT:-""}
    shift 2 || true
    local command="$@"

    if [ -z "$loops" -o -z "$sleeptime" -o -z "$command" ]; then
        echo "wait_for is missing a required parameter"
        return 1
    fi

    local i=0
    while [ $i -lt $loops ]; do
        i=$((i + 1))
        local status=0
        local output=$(eval $command 2>&1) || status=$?
        if [[ -n "$SUCCESSFUL_MATCH_OUTPUT" ]] \
            && [[ $output =~ $SUCCESSFUL_MATCH_OUTPUT ]]; then
            return 0
        elif [[ -n "$FAIL_MATCH_OUTPUT" ]] \
            && [[ $output =~ $FAIL_MATCH_OUTPUT ]]; then
            echo "Command output matched '$FAIL_MATCH_OUTPUT'."
            exit 1
        elif [[ -z "$SUCCESSFUL_MATCH_OUTPUT" ]] && [[ $status -eq 0 ]]; then
            return 0
        fi
        sleep $sleeptime
    done
    local seconds=$((loops * sleeptime))
    printf 'Timing out after %d seconds:\ncommand=%s\nOUTPUT=%s\n' \
        "$seconds" "$command" "$output"
    exit 1
}

# Helper function to `wait_for` that only succeeds when the given regex is
# matching the command's output. Exit early with a failure when the second
# supplied regexp is matching the output.
#
# Example:
#     wait_for_output_unless CREATE_COMPLETE CREATE_FAIL 30 10 heat stack-show undercloud
wait_for_output_unless() {
    SUCCESSFUL_MATCH_OUTPUT=$1
    FAIL_MATCH_OUTPUT=$2
    shift 2
    wait_for $@
    local status=$?
    unset SUCCESSFUL_MATCH_OUTPUT
    unset FAIL_MATCH_OUTPUT
    return $status
}

# Helper function to `wait_for` that only succeeds when the given regex is
# matching the command's output.
#
# Example:
#     wait_for_output CREATE_COMPLETE 30 10 heat stack-show undercloud
wait_for_output() {
    local expected_output=$1
    shift
    wait_for_output_unless $expected_output '' $@
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
# Optionally takes a database name to check for. Defaults to 'mysql'.
check_for_db() {
    local database=${1:-mysql}
    check_required_vars MARIADB_SERVICE_HOST DB_ROOT_PASSWORD

    mysql -h ${MARIADB_SERVICE_HOST} -u root -p"${DB_ROOT_PASSWORD}" \
            -e "select 1" $database > /dev/null 2>&1 || {
        echo "ERROR: database $database is not available @ $MARIADB_SERVICE_HOST" >&2
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

