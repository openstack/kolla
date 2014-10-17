#!/bin/sh

set -e

. /opt/kolla/config-nova-compute.sh

exec /usr/bin/nova-compute
