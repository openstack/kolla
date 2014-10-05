#!/bin/bash -e                                                                                         

: ${CINDER_DB_USER%:=cinder}
: ${CINDER_DB_NAME:=cinder}
: ${KEYSTONE_AUTH_PROTOCOL:=http}
: ${CINDER_KEYSTONE_USER:=cinder}
: ${ADMIN_TENANT_NAME:=admin}

if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
    echo "*** Missing KEYSTONE_ADMIN_TOKEN" >&2
        exit 1
fi

if ! [ "$DB_ROOT_PASSWORD" ]; then
        echo "*** Missing DB_ROOT_PASSWORD" >&2
        exit 1
fi

if ! [ "$CINDER_DB_PASSWORD" ]; then
        CINDER_DB_PASSWORD=$(openssl rand -hex 15)
        export CINDER_DB_PASSWORD
fi

mysql -h ${MARIADB_PORT_3306_TCP_ADDR} -u root \
        -p${DB_ROOT_PASSWORD} mysql <<EOF
EOF                                                                
CREATE DATABASE IF NOT EXISTS ${CINDER_DB_NAME};                                                        
GRANT ALL PRIVILEGES ON glance* TO                                                                      
        '${CINDER_DB_USER}'@'%' IDENTIFIED BY '${CINDER_DB_PASSWORD}'                                   
EOF

#-----Cinder.conf setup-----

# Cinder database
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
	db_driver \
	"cinder.db"

# Rabbit
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
	rabbit_host \
	"127.0.0.1"
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
	rabbit_port \
	"5672"
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
	rabbit_hosts \
	"127.0.0.1:5672"
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
	rabbit_userid \
	"guest"
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
        rabbit_password \
	"guest"
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \
	rabbit_virtual_host \
	"/"
crudini --set /etc/cinder/cinder.conf \ 
	DEFAULT \	
	rabbit_ha_queues \
	"False"

# backend
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	rpc_backend \
	"cinder.openstack.common.rpc.impl_kombu"

# control_exchange
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	control_exchange \
	"openstack"

# osapi
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
        osapi_volume_listen \
	"0.0.0.0"

# api_paste_config
crudini --set /etc/cinder/cinder.conf \
	DEFUALT \
	api_paste_config \
        "/etc/cinder/api-paste.ini"

# auth_strategy
crudini --set /etc/cinder/cinder.conf \
	DEFUALT \
	auth_strategy \
	"keystone"

# debug
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	debug \
	"False"

# verbose
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
        verbose \
	"True"

# logs
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	log_dir \
	"/var/log/cinder/"
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	log_file \
	"/var/log/cinder/cinder.log"

# use_sysloge
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	use_syslog \
	"False"

# iscsi
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	iscsi_ip_address \
	"127.0.0.1"
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
    	iscsi_helper \
	"tgtadm"

# volume_group
crudini --set /etc/cinder/cinder.conf \
	DEFAULT \
	volume_group \
    	"cinder-volumes"


export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="${KEYSTONE_AUTH_PROTOCOL}://${KEYSTONEMASTER_35357_PORT_35357_TCP_ADDR}:35357/v2.0"

/bin/keystone user-create --name ${CINDER_KEYSTONE_USER} --pass ${CINDER_ADMIN_PASSWORD}
/bin/keystone role-create --name ${CINDER_KEYSTONE_USER}
/bin/keystone user-role-add --user ${CINDER_KEYSTONE_USER} --role admin --tenant ${ADMIN_TENANT_NAME}

exec /usr/bin/cinder-all

