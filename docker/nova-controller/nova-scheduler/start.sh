#!/bin/sh

set -e

. /opt/kolla/config-nova.sh

exec /usr/bin/nova-scheduler
