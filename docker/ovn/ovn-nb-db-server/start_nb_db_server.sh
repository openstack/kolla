#!/bin/bash

ovsdb_ip=$1
ovnnb_port=$2
if [ -e $ovnnb_port  ]; then
    ovnnb_port=6641
fi

/usr/sbin/ovsdb-server /var/lib/openvswitch/ovnnb.db -vconsole:emer -vsyslog:err -vfile:info \
--remote=punix:/run/openvswitch/ovnnb_db.sock --remote=ptcp:$ovnnb_port:$ovsdb_ip \
--unixctl=/run/openvswitch/ovnnb_db.ctl --log-file=/var/log/kolla/openvswitch/ovsdb-server-nb.log
