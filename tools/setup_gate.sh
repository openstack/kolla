#!/bin/bash

set -o xtrace
set -o errexit

# Enable unbuffered output for Ansible in Jenkins.
export PYTHONUNBUFFERED=1

function setup_registry {
    sudo mkdir /opt/kolla_registry
    sudo chmod -R 644 /opt/kolla_registry
    docker run -d -p 4000:5000 --restart=always -v /opt/kolla_registry/:/var/lib/registry --name registry registry:2
}

setup_registry
