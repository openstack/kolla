Cinder in Kolla
===============

Overview
--------
Currently Kolla can deploy the cinder services:

- cinder-api
- cinder-scheduler
- cinder-backup
- cinder-volume

The cinder implementation defaults to using LVM storage.  The default
implementation requires a volume group be set up.  This can either be
a real physical volume or a loopback mounted file for development.

Create a Volume Group
---------------------
Use pvcreate and vgcreate to create the volume group.  For example with
the devices /dev/sdb and /dev/sdc:

::

    <WARNING ALL DATA ON /dev/sdb and /dev/sdc will be LOST!>

    pvcreate /dev/sdb /dev/sdc
    vgcreate cinder-volumes /dev/sdb /dev/sdc

During development, it may be desirable to use file backed block storage.  It
is possible to use a file and mount it as a block device via the loopback
system.

::

    mknod /dev/loop2 b 7 2
    dd if=/dev/zero of=/var/lib/cinder_data.img bs=1G count=20
    losetup /dev/loop2 /var/lib/cinder_data.img
    pvcreate /dev/loop2
    vgcreate cinder-volumes /dev/loop2

Validation
----------

Create a volume as follows:

::

    $ openstack volume create  --size 1 steak_volume
    <bunch of stuff printed>

Verify it is available.  If it says "error" here something went wrong during
LVM creation of the volume.

::

    $ openstack volume list
    +--------------------------------------+--------------+-----------+------+-------------+
    | ID                                   | Display Name | Status    | Size | Attached to |
    +--------------------------------------+--------------+-----------+------+-------------+
    | 0069c17e-8a60-445a-b7f0-383a8b89f87e | steak_volume | available |    1 |             |
    +--------------------------------------+--------------+-----------+------+-------------+

Attach the volume to a server using:

::

    openstack server add volume steak_server 0069c17e-8a60-445a-b7f0-383a8b89f87e

Check the console log added the disk:

::

    openstack console log show steak_server

A /dev/vdb should appear in the console log, at least when booting cirros.
If the disk stays in the available state, something went wrong during the
iSCSI mounting of the volume to the guest VM.

Cinder LVM2 backend with iSCSI
------------------------------
As of Newton-1 milestone, Kolla supports LVM2 as cinder backend. It is
accomplished by introducing two new containers tgtd and iscsid.
tgtd container serves as a bridge between cinder-volume process and a server
hosting Logical Volume Groups (LVG). iscsid container serves as a bridge
between nova-compute process and the server hosting LVG.

There are two methods to apply new configuration to cinder:
 1 - New deployments: create cinder.conf and place it at /etc/kolla/config
     folder, then add below configuration lines and run kolla deloyment.
 2 - Existing cinder deployments: modify cinder.conf located at
     /etc/kolla/config by adding below configuration lines and run kolla
     reconfigure.

::

    [DEFAULT]
    enabled_backends = {local_lvm_name}
    volume_name_template=volume-%s

    [{local_lvm_name}]
    lvm_type = default
    volume_group = {lvg_name}
    volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
    volume_backend_name = {local_lvm_name}
    iscsi_helper=tgtadm
    iscsi_ip_address={management_ip_address_of_server_hosting_LVG}
    iscsi_protocol=iscsi
::

Where:

- local_lvm_name is a name chosen by a user for a spefic LVM2 backend, multiple
LVM2 backend can be confiugred and each should have a unique name.

- lvg_name is a name Logical Volume Group created for cinder to store volumes.

- management_ip_address_of_server_hosting_LVG is IP address of an interface
where cinder process is bound to. (Do not use VIP address here, LVG does not
move from server to server as VIP address does in case of a server failure).

NOTE: For Ubuntu and LVM2/iSCSI

iscsd process uses configfs which is normally mounted at /sys/kernel/config to
store discovered targets information, on centos/rhel type of systems this special
file system gets mounted automatically, which is not the case on debian/ubuntu.
Since iscsid container runs on every nova compute node, the following steps must
be completed on every Ubuntu server targeted for nova compute role.

 1 - Add configfs module to /etc/modules
 2 - Rebuild initramfs using: "update-initramfs -u" command
 3 - Make sure configfs gets mounted during a server boot up process. There are
     multiple ways to accomplish it, one example is adding this command to
     "mount -t configfs configfs /sys/kernel/config" to /etc/rc.local

