#!/bin/bash

set -o errexit
set -o xtrace

# exist when the jobs is not project jobs.
if [[ -z $IN_PROJECT_JOBS ]]; then
    exit 0
fi

tools/setup_gate.sh
tox -e $ACTION-$BASE_DISTRO-$INSTALL_TYPE

if [[ -n $PACK_REGISTRY ]] && [[ $ACTION == "build" ]]; then
    pack_registry
fi
