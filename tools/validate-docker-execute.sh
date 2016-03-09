#!/bin/bash
#
# This script can be used to check user privilege to execute
# docker commands

function check_dockerexecute {
    docker ps &>/dev/null
    return_val=$?
    if [ $return_val -ne 0 ]; then
        echo "User $USER can't seem to run Docker commands. Verify product documentation to allow user to execute docker commands" 1>&2
        exit 1
    fi
}
check_dockerexecute
