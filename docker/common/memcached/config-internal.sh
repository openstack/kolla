#!/bin/bash

set -o errexit

CMD="/usr/bin/memcached"
ARGS="-u memcached -vv"

exec $CMD $ARGS
