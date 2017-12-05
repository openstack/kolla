#!/bin/bash

RES=0

for dockerfile in "$@"; do
    if grep -qE '^\s+[A-Z]+\s' "$dockerfile"; then
        echo "ERROR: $dockerfile has indented Dockerfile instruction" >&2
        RES=1
    fi
done

exit $RES
