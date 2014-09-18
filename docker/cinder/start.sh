#!/bin/bash -e                                                                                         
env > /root/ENV

# mariadb
#socat UNIX-LISTEN:/var/lib/mysql/mysql.sock,fork,reuseaddr,unlink-early,user=mysql,group=mysql,mode=777TCP:127.0.0.1:3306 &                                                                                  
#/usr/bin/openstack-db --service cinder --init --yes --rootpw ${DB_ROOT_PASSWORD} --password redhat 

# sqlite replace with mariadb above
#sed -ri 's/#connection=sqlite:////cinder/openstack/common/db/$sqlite_db/connection=sqlite:\/\/\/cinder.db/' /etc/cinder/cinder.conf                                                                          
sed -ri 's/#connection=*/connection=sqlite:\/\/\/cinder.db/' /etc/cinder/cinder.conf

#-----Cinder.conf setup-----

# Cinder database
sed -ri 's/#db_driver=cinder.db/db_driver=cinder.db/' /etc/cinder/cinder.conf

# Rabbit
sed -ri 's/#rabbit_host=127.0.0.1/rabbit_host=127.0.0.1/' /etc/cinder/cinder.conf
sed -ri 's/#rabbit_port=5672/rabbit_port=127.0.0.1/' /etc/cinder/cinder.conf
sed -ri 's/#rabbit_hosts=127.0.0.1:5672/rabbit_hosts=127.0.0.1:5672/' /etc/cinder/cinder.conf
sed -ri 's/#rabbit_userid=guest/rabbit_userid=guest/' /etc/cinder/cinder.conf
sed -ri 's/#rabbit_password=guest/rabbit_password=guest/' /etc/cinder/cinder.conf
sed -ri 's/#rabbit_virtual_host=\/\/rabbit_virtual_host=\/\/' /etc/cinder/cinder.conf
sed -ri 's/#rabbit_ha_queues=False/rabbit_ha_queues=False/' /etc/cinder/cinder.conf

# backend
sed -ri 's/#rpc_backend=cinder.openstack.common.rpc.impl_kombu/rpc_backend=cinder.openstack.common.rpc.impl_kombu/' /etc/cinder/cinder.conf

# control_exchange
sed -ri 's/#control_exchange=openstack/control_exchange=openstack/' /etc/cinder/cinder.conf

# osapi
sed -ri 's/#osapi_volume_listen=0.0.0.0/osapi_volume_listen=0.0.0.0/' /etc/cinder/cinder.conf

# api_paste_config
sed -ri 's/#api_paste_config=api-paste.ini/api_paste_config=/etc/cinder/api-paste.ini/' /etc/cinder/cinder.conf

# auth_strategy
sed -ri 's/#auth_strategy=noauth/auth_strategy=keystone/' /etc/cinder/cinder.conf

# debug
sed -ri 's/#debug=false/debug=false/' /etc/cinder/cinder.conf

# verbose
sed -ri 's/#verbose=true/verbose=true/' /etc/cinder/cinder.conf

# log_dir
sed -ri 's/#log_dir=<None>/log_dir=/var/log/cinder/' /etc/cinder/cinder.conf

# use_syslog
sed -ri 's/#use_syslog=false/use_syslog=false/' /etc/cinder/cinder.conf

# iscsi
sed -ri 's/#iscsi_ip_address=127.0.0.1/iscsi_ip_address=127.0.0.1/' /etc/cinder/cinder.conf
sed -ri 's/#iscsi_helper=tgtadm/iscsi_helper=tgtadm/' /etc/cinder/cinder.conf

# volume_group
sed -ri 's/#volume_group=cinder-volumes/volume_group=cinder-volumes/' /etc/cinder/cinder.conf

# sql
#sed -ri 's/#sql_connection=mysql://cinder:bc8cafb03d64404b@127.0.0.1/cinder/sql_connection=mysql://cinder:bc8cafb03d64404b@127.0.0.1/cinder/' /etc/cinder/cinder.conf                                        
#sed -ri 's/#sql_idle_timeout=3600/sql_idle_timeout=3600/' /etc/cinder/cinder.conf

# timeout
sed -ri 's/#idle_timeout=3600/idle_timeout=200/' /etc/cinder/cinder.conf

/usr/bin/cinder-manage db_sync

/usr/bin/cinder-all &
PID=$!

/bin/sleep 5

export SERVICE_TOKEN=`cat /root/ks_admin_token`
export SERVICE_ENDPOINT="http://127.0.0.1:35357/v2.0"

#/bin/keystone user-create --name admin --pass redhat                                                  
#/bin/keystone role-create --name admin                                                                
#/bin/keystone tenant-create --name admin                                                             
#/bin/keystone user-role-add --user admin --role admin --tenant admin                                 

kill -TERM $PID

echo "starting cinder-all.."
exec /usr/bin/cinder-all

