#!/bin/bash
set -e

: ${HORIZON_KEYSTONE_USER:=horizon}

. /opt/kolla/kolla-common.sh

check_for_keystone
check_for_glance
check_for_nova

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

cfg=/etc/openstack-dashboard/local_settings

sed -ri 's/ALLOWED_HOSTS = \['\''horizon.example.com'\'', '\''localhost'\''\]/ALLOWED_HOSTS = \['\''*'\'', \]/' /etc/openstack-dashboard/local_settings

sed -ri 's/OPENSTACK_KEYSTONE_URL = \"http:\/\/%s:5000\/v2.0\" % OPENSTACK_HOST/OPENSTACK_KEYSTONE_URL = \"http:\/\/'"$KEYSTONE_PUBLIC_SERVICE_HOST"':5000\/v2.0\"/' /etc/openstack-dashboard/local_settings

sed -ri 's/OPENSTACK_HOST = \"127.0.0.1\"/OPENSTACK_HOST = \"'"$KEYSTONE_PUBLIC_SERVICE_HOST"'\" /' /etc/openstack-dashboard/local_settings

/usr/sbin/httpd -DFOREGROUND
