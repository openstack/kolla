#!/bin/sh

sh /opt/heat/config-glance.sh api

exec /usr/bin/heat-api
