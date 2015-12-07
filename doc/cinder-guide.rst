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
