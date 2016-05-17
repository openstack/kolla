#!/bin/bash

REAL_PATH=$(python -c "import os,sys;print os.path.realpath('$0')")
cd "$(dirname "$REAL_PATH")/.."

find docker -name Dockerfile.j2 -print0 |
    xargs -0 tools/validate-maintainer.sh || exit 1

find docker -name Dockerfile.j2 -print0 |
    xargs -0 tools/validate-install-command.sh || exit 1

