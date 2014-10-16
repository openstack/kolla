#!/bin/sh

set -e

. /opt/kolla/config-nova-controller.sh

exec /usr/bin/nova-scheduler
