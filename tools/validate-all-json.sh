#!/bin/sh

TOPLEVEL=$(git rev-parse --show-toplevel)

cd $TOPLEVEL

git ls-files -z '*.json' |
    xargs -0 python tools/validate-json.py || exit 1

