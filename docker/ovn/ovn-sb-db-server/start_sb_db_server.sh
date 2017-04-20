#!/bin/bash

ovnsb_db_ip=$1
ovnsb_port=$2
if [ -e $ovnsb_port  ]; then
    ovnsb_port=6642
fi

/usr/sbin/ovsdb-server /var/lib/openvswitch/ovnsb.db -vconsole:emer -vsyslog:err -vfile:info \
--remote=punix:/run/openvswitch/ovnsb_db.sock --remote=ptcp:$ovnsb_port:$ovnsb_db_ip \
--unixctl=/run/openvswitch/ovnsb_db.ctl --log-file=/var/log/kolla/openvswitch/ovsdb-server-sb.log
