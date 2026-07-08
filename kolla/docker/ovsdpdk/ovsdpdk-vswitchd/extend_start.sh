#!/bin/bash

# using userspace netdev datapath so do not loading ovs kernel module
# chmod openvsitch run directory so libvirt can create vhost-user sockets.
chmod 777 /var/run/openvswitch

