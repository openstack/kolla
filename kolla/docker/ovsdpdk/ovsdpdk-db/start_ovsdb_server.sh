#!/bin/bash

# NOTE: (sbezverk) ovs_bridge and ovs_ext_intf variables get initialized only when
# this script is executed for kubernetes deployment. With Ansible deployment, only
# ovsdb-server gets launched and then the following workflow step will create
# an external bridge and plug an external interface. With Kubernetes we want to
# leverage its dynamic nature of automatic scaling up and down. It means all
# activities related to creating initial bridge, plugging external interface
# must be done by DaemonSet launched container.

ovsdb_ip=$1
ovs_bridge=$2
ovs_ext_intf=$3

# NOTE: (sbezverk) The reason for introducing this script is to be able
# to launch ovsdb-server and to create the initial external bridge in one step.
# It is required in order to be able to use DaemonSet.

if [ ! -e $ovs_bridge  ] && [ ! -e $ovs_ext_intf  ]; then
# NOTE: (sbezverk) This part is executed only by kubernetes deployment.
# Creating external bridge
    /usr/sbin/ovsdb-server /var/lib/openvswitch/conf.db --remote=punix:/var/run/openvswitch/db.sock --run="ovs-vsctl --no-wait --db=unix:/var/run/openvswitch/db.sock add-br $ovs_bridge"
# Plug the external interface into the external bridge.
    /usr/sbin/ovsdb-server /var/lib/openvswitch/conf.db --remote=punix:/var/run/openvswitch/db.sock --run="ovs-vsctl --no-wait --db=unix:/var/run/openvswitch/db.sock add-port $ovs_bridge $ovs_ext_intf"
# Run ovsdb server process
    /usr/sbin/ovsdb-server /var/lib/openvswitch/conf.db -vconsole:emer -vsyslog:err -vfile:info --remote=punix:/var/run/openvswitch/db.sock --remote=ptcp:6640 --log-file=/var/log/kolla/openvswitch/ovsdb-server.log
else
# NOTE: (sbezverk) This part is executed only by kolla-ansible deployment.
    /usr/sbin/ovsdb-server /var/lib/openvswitch/conf.db -vconsole:emer -vsyslog:err -vfile:info --remote=punix:/run/openvswitch/db.sock --remote=ptcp:6640:$ovsdb_ip --log-file=/var/log/kolla/openvswitch/ovsdb-server.log
fi
