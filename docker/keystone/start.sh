#!/bin/bash

# Exit the container if MariaDB is not yet up - then depend on kube to restart
if [ -z "$MARIADB_PORT_3306_TCP_PORT" ]; then
    exit 1
fi

: ${KEYSTONE_ADMIN_PASSWORD:=kolla}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
    KEYSTONE_ADMIN_TOKEN=$(openssl rand -hex 15)
fi

if ! [ "$KEYSTONE_DB_PASSWORD" ]; then
    KEYSTONE_DB_PASSWORD=$(openssl rand -hex 15)
fi

mysql -h ${MARIADB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS keystone;
GRANT ALL PRIVILEGES ON keystone.* TO
    'keystone'@'%' IDENTIFIED BY '${KEYSTONE_DB_PASSWORD}'
EOF

crudini --set /etc/keystone/keystone.conf \
    database \
    connection \
    "mysql://keystone:${KEYSTONE_DB_PASSWORD}@${MARIADB_PORT_3306_TCP_ADDR}:${MARIADB_PORT_3306_TCP_PORT}/keystone"
crudini --set /etc/keystone/keystone.conf \
    DEFAULT \
    admin_token \
    "${KEYSTONE_ADMIN_TOKEN}"
crudini --del /etc/keystone/keystone.conf \
    DEFAULT \
    log_file
crudini --del /etc/keystone/keystone.conf \
    DEFAULT \
    log_dir
crudini --set /etc/keystone/keystone.conf DEFAULT use_stderr True

cat /etc/keystone/keystone.conf

/usr/bin/keystone-manage db_sync
/usr/bin/keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

MY_IP=$(ip route get $(ip route | awk '$1 == "default" {print $3}') |
    awk '$4 == "src" {print $5}')
if [ -z "$KEYSTONE_ADMIN_PORT_35357_TCP_ADDR" ]; then
    KEYSTONE_ADMIN_PORT_35357_TCP_ADDR=$MY_IP
fi
if [ -z "$KEYSTONE_PUBLIC_PORT_5000_TCP_ADDR" ]; then
    KEYSTONE_PUBLIC_PORT_5000_TCP_ADDR=$MY_IP
fi

/usr/bin/keystone-all &
PID=$!

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://127.0.0.1:35357/v2.0"
SERVICE_ENDPOINT_ADMIN="http://${KEYSTONE_ADMIN_PORT_35357_TCP_ADDR}:35357/v2.0"
SERVICE_ENDPOINT_USER="http://${KEYSTONE_PUBLIC_PORT_5000_TCP_ADDR}:5000/v2.0"

# wait for keystone to become active
while ! curl -o /dev/null -s --fail ${SERVICE_ENDPOINT}; do
    sleep 1;
done

crux user-create --update \
    -n admin -p "${KEYSTONE_ADMIN_PASSWORD}" \
    -t admin -r admin
crux endpoint-create --remove-all \
    -n keystone -t identity \
    -I "${SERVICE_ENDPOINT_USER}" \
    -A "${SERVICE_ENDPOINT_ADMIN}"

kill -TERM $PID

echo "Running keystone service."
exec /usr/bin/keystone-all
