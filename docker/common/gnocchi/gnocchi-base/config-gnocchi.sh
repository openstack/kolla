#!/bin/bash

set -e
. /opt/kolla/kolla-common.sh

check_required_vars KEYSTONE_ADMIN_TOKEN KEYSTONE_ADMIN_SERVICE_HOST \
                    KEYSTONE_ADMIN_SERVICE_PORT KEYSTONE_PUBLIC_SERVICE_HOST \
                    GNOCCHI_STORAGE_BACKEND GNOCCHI_DATA_DIR GNOCCHI_SERVICE_PORT
dump_vars

cat > /openrc <<EOF
export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONE_ADMIN_SERVICE_HOST}:${KEYSTONE_ADMIN_SERVICE_PORT}/v2.0"
EOF


cfg=/etc/gnocchi/gnocchi.conf
crudini --set $cfg \
    storage driver "$GNOCCHI_STORAGE_BACKEND"
crudini --set $cfg \
    storage file_basepath "$GNOCCHI_DATA_DIR"
crudini --set $cfg \
    indexer url "mysql://$GNOCCHI_DB_USER:$GNOCCHI_DB_PASSWORD@$MARIADB_SERVICE_HOST/$GNOCCHI_DB_NAME?charset=utf8"
