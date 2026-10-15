#!/bin/bash

if [[ ! -d "/run/ovn" ]]; then
    mkdir -p /run/ovn
fi

. /usr/local/bin/kolla_ovn_extend_start
