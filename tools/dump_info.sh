#!/bin/bash

set -o xtrace

function dump_node_info {
    # NOTE(SamYaple): function for debugging gate
    set +o errexit
    local OLD_PATH="${PATH}"
    PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    sudo parted -l

    sudo mount

    df -h

    uname -a

    cat /etc/*release*

    cat /proc/meminfo

    PATH="${OLD_PATH}"
    set -o errexit
}

(dump_node_info 2>&1) > /tmp/logs/node_info_$(date +%s)
