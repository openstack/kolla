#!/bin/bash

RES=0

for dockerfile in "$@"; do
    if grep "apt-get install\|dnf install" "$dockerfile"; then
        echo "ERROR: $dockerfile has incorrectly formatted install command Should be in the form 'apt-get|dnf -y install ...'" >&2
        RES=1
    fi
done

exit $RES
