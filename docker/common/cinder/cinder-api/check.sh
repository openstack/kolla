#!/bin/sh

RES=0

. /openrc
if ! keystone token-get > /dev/null; then
    echo "ERROR: keystone token-get failed" >&2
    RES=1
else
    if ! cinder list > /dev/null; then
        echo "ERROR: cinder list failed" >&2
        RES=1
    fi
fi

exit $RES
