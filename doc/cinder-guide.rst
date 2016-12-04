.. _cinder-guide:

===============
Cinder in Kolla
===============

Overview
========

Currently Kolla can deploy the cinder services:

  - cinder-api
  - cinder-scheduler
  - cinder-backup
  - cinder-volume

The cinder implementation defaults to using LVM storage. The default
implementation requires a volume group be set up. This can either be
a real physical volume or a loopback mounted file for development.

.. note ::
  The Cinder community has closed a bug as WontFix which makes it
  impossible for LVM to be used at all in a multi-controller setup.
  The only option for multi-controller storage to work correctly at
  present is via a Ceph deployment. If community members disagree
  with this decision, please report the specific use case in the
  Cinder bug tracker here:
  `_bug 1571211 <https://launchpad.net/bugs/1571211>`__.


Create a Volume Group
=====================
Use ``pvcreate`` and ``vgcreate`` to create the volume group. For example
with the devices ``/dev/sdb`` and ``/dev/sdc``:

::

    <WARNING ALL DATA ON /dev/sdb and /dev/sdc will be LOST!>

    pvcreate /dev/sdb /dev/sdc
    vgcreate cinder-volumes /dev/sdb /dev/sdc

During development, it may be desirable to use file backed block storage. It
is possible to use a file and mount it as a block device via the loopback
system. ::

    mknod /dev/loop2 b 7 2
    dd if=/dev/zero of=/var/lib/cinder_data.img bs=1G count=20
    losetup /dev/loop2 /var/lib/cinder_data.img
    pvcreate /dev/loop2
    vgcreate cinder-volumes /dev/loop2

Validation
==========

Create a volume as follows:

::

    $ openstack volume create --size 1 steak_volume
    <bunch of stuff printed>

Verify it is available. If it says "error" here something went wrong during
LVM creation of the volume. ::

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

A ``/dev/vdb`` should appear in the console log, at least when booting cirros.
If the disk stays in the available state, something went wrong during the
iSCSI mounting of the volume to the guest VM.

Cinder LVM2 back end with iSCSI
===============================

As of Newton-1 milestone, Kolla supports LVM2 as cinder back end. It is
accomplished by introducing two new containers ``tgtd`` and ``iscsid``.
``tgtd`` container serves as a bridge between cinder-volume process and a
server hosting Logical Volume Groups (LVG). ``iscsid`` container serves as
a bridge between nova-compute process and the server hosting LVG.

In order to use Cinder's LVM back end, a LVG named ``cinder-volumes`` should
exist on the server and following parameter must be specified in
``globals.yml`` ::

    enable_cinder_backend_lvm: "yes"

For Ubuntu and LVM2/iSCSI
~~~~~~~~~~~~~~~~~~~~~~~~~

``iscsd`` process uses configfs which is normally mounted at
``/sys/kernel/config`` to store discovered targets information, on centos/rhel
type of systems this special file system gets mounted automatically, which is
not the case on debian/ubuntu. Since ``iscsid`` container runs on every nova
compute node, the following steps must be completed on every Ubuntu server
targeted for nova compute role.

  - Add configfs module to ``/etc/modules``
  - Rebuild initramfs using: ``update-initramfs -u`` command
  - Stop ``open-iscsi`` system service due to its conflicts
    with iscsid container.

    For Ubuntu 14.04 (upstart): ``service open-iscsi stop``

    Ubuntu 16.04 (systemd):
    ``systemctl stop open-iscsi; systemctl stop iscsid``

  - Make sure configfs gets mounted during a server boot up process. There are
    multiple ways to accomplish it, one example:
    ::

      mount -t configfs /etc/rc.local /sys/kernel/config

Cinder back end with external iSCSI storage
===========================================

In order to use external storage system (like one from EMC or NetApp)
the following parameter must be specified in ``globals.yml`` ::

    enable_cinder_backend_iscsi: "yes"

Also ``enable_cinder_backend_lvm`` should be set to "no" in this case.
