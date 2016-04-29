#!/bin/bash

REAL_PATH=$(python -c "import os,sys;print os.path.realpath('$0')")
cd "$(dirname "$REAL_PATH")/.."

find . -path ./.tox -prune -name '*.json' -print0 |
    xargs -0 python tools/validate-json.py || exit 1
