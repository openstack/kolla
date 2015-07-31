# Storage Guide

This is a overview of how Cinder is implemented in Kolla so that it is easier
to understand how to use it. Keep in mind, this is the first iteration for
Cinder as support for Ceph and physical devices will follow.

## Overview

Kolla's setup for Cinder uses tgtd as the default iSCSI helper to implement
persistent targets.  By default, we use a loop back file that is defined by
CINDER_LVM_LO_VOLUME_SIZE to create the cinder-volumes volume group.

## Configure Cinder

Listed below are the default configurations for Cinder.  For more info on what
each variable does look at the [integration guide.](https://github.com/stackforge/kolla/blob/master/docs/integration-guide.md):

    # Cinder Volume
    CINDER_ENABLED_BACKEND=lvm57
    CINDER_LVM_LO_VOLUME_SIZE=4G
    CINDER_VOLUME_API_LISTEN=$HOST_IP
    CINDER_VOLUME_BACKEND_NAME=LVM_iSCSI57
    CINDER_VOLUME_DRIVER=cinder.volume.drivers.lvm.LVMISCSIDriver
    CINDER_VOLUME_GROUP=cinder-volumes
    ISCSI_HELPER=tgtadm
    ISCSI_IP_ADDRESS=$HOST_IP

## Using Cinder

After you've started all your containers, you should be able to interact
with Cinder.

    cinder list

Next, you will want to create a volume and attach it to a running instance.

    cinder create 1
    nova volume-attach <instance_id> <volume_id>

## Debugging and deleting volumes

The cinder-volumes volume group can't be seen from the host.  In order to
interact with an existing volume, you need to jump into the Cinder Volume
container.

    sudo docker exec -it <cinder_volume_container> /bin/bash
    vgs

Running 'vgs' will list the volumes groups.  From there, you can look
specific volumes to make sure volume creation succeeded.

To delete the cinder-volumes volume group from within the container run:

    vgs remove cinder-volumes
