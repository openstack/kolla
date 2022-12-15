#!/bin/bash

# Move to top level directory
REAL_PATH=$(realpath $0)
cd "$(dirname "$REAL_PATH")/.."

RES=0

find docker -name Dockerfile.j2 -print0 |
    xargs -0 tools/validate-maintainer.sh || RES=1

find docker -name Dockerfile.j2 -print0 |
    xargs -0 tools/validate-install-command.sh || RES=1

find docker -name Dockerfile.j2 -print0 |
    xargs -0 tools/validate-indentation.sh || RES=1

exit $RES
