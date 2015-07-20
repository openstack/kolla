#!/bin/bash

set -e

. /opt/kolla/kolla-common.sh

check_required_vars ADMIN_TENANT_NAME \
                    GLANCE_DB_NAME \
                    GLANCE_DB_PASSWORD \
                    GLANCE_DB_USER \
                    GLANCE_KEYSTONE_PASSWORD \
                    GLANCE_KEYSTONE_USER \
                    KEYSTONE_PUBLIC_SERVICE_HOST \
                    MARIADB_SERVICE_HOST
dump_vars

cat > /openrc <<EOF
export OS_AUTH_URL="http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/v2.0"
export OS_USERNAME="${GLANCE_KEYSTONE_USER}"
export OS_PASSWORD="${GLANCE_KEYSTONE_PASSWORD}"
export OS_TENANT_NAME="${ADMIN_TENANT_NAME}"
EOF

for cfg in /etc/glance/glance-api.conf /etc/glance/glance-registry.conf; do
    crudini --set $cfg \
        DEFAULT \
        log_file \
        ""

    for option in auth_protocol auth_host auth_port; do
        crudini --del $cfg \
            keystone_authtoken \
            $option
    done

    crudini --set $cfg \
        keystone_authtoken \
        auth_uri \
        "http://${KEYSTONE_PUBLIC_SERVICE_HOST}:5000/"
    crudini --set $cfg \
        keystone_authtoken \
        admin_tenant_name \
        "${ADMIN_TENANT_NAME}"
    crudini --set $cfg \
        keystone_authtoken \
        admin_user \
        "${GLANCE_KEYSTONE_USER}"
    crudini --set $cfg \
        keystone_authtoken \
        admin_password \
        "${GLANCE_KEYSTONE_PASSWORD}"

    crudini --set $cfg \
        paste_deploy \
        flavor \
        keystone

    crudini --set $cfg \
        database \
        connection \
        "mysql://${GLANCE_DB_USER}:${GLANCE_DB_PASSWORD}@${MARIADB_SERVICE_HOST}/${GLANCE_DB_NAME}"
done
