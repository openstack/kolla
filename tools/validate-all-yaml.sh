#!/bin/bash

# Move to top level directory
REAL_PATH=$(realpath $0)
cd "$(dirname "$REAL_PATH")/.."

find . -name '*.yaml' -o -name '*.yml' -print0 |
    xargs -0 python3 tools/validate-yaml.py || exit 1
