#!/bin/bash

RES=0

. /openrc
if ! keystone token-get > /dev/null; then
    echo "ERROR: keystone token-get failed" >&2
    RES=1
else
    if ! nova list > /dev/null; then
        echo "ERROR: nova list failed" >&2
        RES=1
    fi
fi

exit $RES

