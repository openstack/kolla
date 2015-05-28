#!/bin/bash
#
# This script is used to setup Kolla Docker environment,
# after running this script, you can run Kolla functional test.
# NOTE: This script was only tested on redhat/debian/suse platform families.
#

set -xu

DOCKER_MIN_VERSION=1.6.0

function check_prerequisites {
    if [[ $EUID -ne 0 ]]; then
        echo "You must execute this script as root." 1>&2
        exit 1
    fi
    if [ "$OSTYPE" != "linux-gnu" ]; then
        echo Platform not supported
        exit 255
    fi
    if [ "$HOSTTYPE" != "x86_64" ]; then
        echo Machine type not supported
        exit 255
    fi
}

function check_docker_version {
    local docker_version
    local result
    if type docker &>/dev/null; then
        docker_version=$(docker --version 2>/dev/null | awk -F"[ ,]" '{print $3}')
        result=$(awk 'BEGIN{print '$docker_version' >= '$DOCKER_MIN_VERSION'}')
        if [ $result = 1 ]; then
            return 0
        fi
    fi
    return 1
}

function start_docker {
    pkill -x -9 docker
    if check_docker_version; then
        docker -d &>/dev/null &
    else
        curl -sSL https://get.docker.com/builds/Linux/x86_64/docker-$DOCKER_MIN_VERSION -o /usr/local/bin/docker
        chmod +x /usr/local/bin/docker
        /usr/local/bin/docker -d &>/dev/null &
    fi
}

function create_group {
    getent group docker
    result=$?
    if [ $result -eq 0 ]; then # 0: key already exists, nothing to do
        return
    elif [ $result -eq 2 ]; then # 2: key could not be found in database
        groupadd docker
        chown root:docker /var/run/docker.sock
        usermod -a -G docker ${SUDO_USER:-$USER}
    else
        echo Unexpected failure: $result
        exit
    fi
}

# Check for root privileges and correct platform
check_prerequisites

# Start Docker service
start_docker

# Ensure executing user is placed in the docker group
create_group
