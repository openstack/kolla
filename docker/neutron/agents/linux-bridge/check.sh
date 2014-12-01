#!/bin/sh

RES=0

if ! /usr/sbin/brctl show; then
    echo "ERROR: brctl show failed" >&2
    RES=1
fi

exit $RES
