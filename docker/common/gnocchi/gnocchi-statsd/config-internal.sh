#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-gnocchi.sh

exec /usr/bin/gnocchi-statsd
