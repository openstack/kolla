#!/bin/sh

sh /opt/glance/config-glance.sh api

exec /usr/bin/glance-api
