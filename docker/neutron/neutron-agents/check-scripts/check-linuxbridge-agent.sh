#!/bin/bash

RES=0

check=$(/usr/bin/neutron agent-list | awk '/ Linux / {print $10}')
error="ERROR: Neutron Linux Bridge agent is not alive."

if [[ $check != ":-)" ]]; then
    echo $error >&2
    RES=1
fi

exit $RES
