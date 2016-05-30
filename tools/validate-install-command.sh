#!/bin/bash

RES=0

for dockerfile in "$@"; do
    if grep "apt-get install\|yum install" "$dockerfile"; then
        echo "ERROR: $dockerfile has incorrectly formatted install command Should be in the form 'apt-get|yum -y install ...'" >&2
        RES=1
    fi
done

exit $RES
