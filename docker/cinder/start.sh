#!/bin/bash -e                                                                                         
env > /root/ENV

# mariadb
#socat UNIX-LISTEN:/var/lib/mysql/mysql.sock,fork,reuseaddr,unlink-early,user=mysql,group=mysql,mode=777TCP:127.0.0.1:3306 &                                                                                  
#/usr/bin/openstack-db --service cinder --init --yes --rootpw ${DB_ROOT_PASSWORD} --password redhat 

# sqlite replace with mariadb above
#crudini --set /etc/cinder/cinder.conf \ DEFAULT connection "sqlite:\/\/\/cinder.db" /etc/cinder/cinder.conf                                                                          
crudini --set /etc/cinder/cinder.conf \ 
	database \
	connection \
	"connection=sqlite:\/\/\/cinder.db/"

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

# sql
#crudini --set /etc/cinder/cinder.conf \ sql_connection \ "mysql://cinder:bc8cafb03d64404b@127.0.0.1/cinder/"
#crudini --set /etc/cinder/cinder.conf \ sql_idle_timeout \ "3600"

# timeout
#crudini --set /etc/cinder/cinder.conf \ idle_timeout \ "200"

/usr/bin/cinder-manage db_sync

/usr/bin/cinder-all &
PID=$!

/bin/sleep 5

export SERVICE_TOKEN=`cat /root/ks_admin_token`
export SERVICE_ENDPOINT="http://127.0.0.1:35357/v2.0"

kill -TERM $PID

echo "starting cinder-all.."
exec /usr/bin/cinder-all

