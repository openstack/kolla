#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# TODO(SamYaple): This check could be much better, but should work for now
if [[ $(hostname | grep rax) ]]; then
    export DEV="xvde"
else
    echo "Assuming this is an hpcloud box"
    export DEV="vdb"
fi

# Just for mandre :)
if [[ ! -f /etc/sudoers.d/jenkins ]]; then
    echo "jenkins ALL=(:docker) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/jenkins
fi

distro=$(awk -F'[="]'+ '/^ID/ {print tolower($2); exit}' /etc/*-release)
exec tests/setup_${distro}.sh
