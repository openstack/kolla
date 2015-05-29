#!/bin/bash
#
# This script is used to setup Kolla Docker environment,
# after running this script, you can run Kolla functional test.
# NOTE: This script was only tested on redhat/debian/suse platform families.
#

set -xeu

DOCKER_MIN_VERSION=1.6.0

function check_platform() {
    if [ "$OSTYPE" != "linux-gnu" ]; then
        echo Platform not supported
        exit 255
    fi
}

function check_docker_version() {
    local docker_version
    local result
    if which docker &>/dev/null; then
        docker_version=$(docker --version 2>/dev/null | awk -F"[ ,]" '{print $3}')
        result=$(awk 'BEGIN{print '$docker_version' >= '$DOCKER_MIN_VERSION'}')
        if [ $result = 1 ]; then
            return 0
        fi
    fi
    return 1
}

function start_docker() {
    pkill -9 docker || true
    if check_docker_version; then
        docker -d &>/dev/null &
    else
        curl -sSL https://get.docker.com/builds/Linux/x86_64/docker-$DOCKER_MIN_VERSION -o /usr/local/bin/docker
        chmod +x /usr/local/bin/docker
        /usr/local/bin/docker -d &>/dev/null &
    fi
}

## Check platfrom
check_platfrom

## Start Docker service
start_docker
