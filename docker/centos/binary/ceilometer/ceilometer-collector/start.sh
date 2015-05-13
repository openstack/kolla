#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh
. /opt/kolla/config-ceilometer.sh


exec /usr/bin/ceilometer-collector
