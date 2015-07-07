#!/bin/bash
set -e

: ${HORIZON_KEYSTONE_USER:=horizon}

. /opt/kolla/kolla-common.sh

fail_unless_os_service_running keystone
fail_unless_os_service_running glance
fail_unless_os_service_running nova

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:35357/v2.0"

cfg=/etc/openstack-dashboard/local_settings
httpdcfg=/etc/httpd/conf.d/openstack-dashboard.conf

sed -ri 's/ALLOWED_HOSTS = \['\''horizon.example.com'\'', '\''localhost'\''\]/ALLOWED_HOSTS = \['\''*'\'', \]/' /etc/openstack-dashboard/local_settings

sed -ri 's/OPENSTACK_KEYSTONE_URL = \"http:\/\/%s:5000\/v2.0\" % OPENSTACK_HOST/OPENSTACK_KEYSTONE_URL = \"http:\/\/'"$KEYSTONE_PUBLIC_SERVICE_HOST"':5000\/v2.0\"/' /etc/openstack-dashboard/local_settings

sed -ri 's/OPENSTACK_HOST = \"127.0.0.1\"/OPENSTACK_HOST = \"'"$KEYSTONE_PUBLIC_SERVICE_HOST"'\" /' /etc/openstack-dashboard/local_settings

# Make sure we launch horizon using the default value for WEBROOT, which is
# '/'.
sed -ri '/^WEBROOT =.+/d' $cfg
sed -ri 's,^(WSGIScriptAlias) /dashboard (/usr/share/openstack-dashboard/openstack_dashboard/wsgi/django.wsgi),\1 / \2,' $httpdcfg
sed -ri 's,^(Alias /dashboard)(/static /usr/share/openstack-dashboard/static),Alias \2,' $httpdcfg

# This step is required because of:
# https://bugzilla.redhat.com/show_bug.cgi?id=1220070
# Running this in the Dockerfile didn't fix the HTTP/500 as a result of the
# missing compress action.
python /usr/share/openstack-dashboard/manage.py compress

/usr/sbin/httpd -DFOREGROUND
