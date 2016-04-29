#!/bin/bash

REAL_PATH=$(python -c "import os,sys;print os.path.realpath('$0')")
cd "$(dirname "$REAL_PATH")/.."

find . -name '*.yaml' -o -name '*.yml' -print0 |
    xargs -0 python tools/validate-yaml.py || exit 1
