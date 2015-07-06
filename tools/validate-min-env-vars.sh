#!/bin/bash

REAL_PATH=$(python -c "import os,sys;print os.path.realpath('$0')")
cd "$(dirname "$REAL_PATH")/.."

MIN_ENV_VARS_DOC=./docs/minimal-environment-vars.md

mv ${MIN_ENV_VARS_DOC}{,.validate}

# Generate a new file and check the content is the same
./tools/min-env.sh
/usr/bin/diff ${MIN_ENV_VARS_DOC}{,.validate}
RET=$?

mv ${MIN_ENV_VARS_DOC}{.validate,}

exit $RET
