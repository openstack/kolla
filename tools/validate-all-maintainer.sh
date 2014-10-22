#!/bin/sh

TOPLEVEL=$(git rev-parse --show-toplevel)

cd $TOPLEVEL

git ls-files -z '*/Dockerfile' |
    xargs -0 tools/validate-maintainer.sh || exit 1

