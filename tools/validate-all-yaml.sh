#!/bin/sh

TOPLEVEL=$(git rev-parse --show-toplevel)

cd $TOPLEVEL

git ls-files -z '*.yaml' |
    xargs -0 python tools/validate-yaml.py || exit 1

