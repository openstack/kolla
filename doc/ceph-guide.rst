.. _ceph-guide:

=============
Ceph in Kolla
=============

The out-of-the-box Ceph deployment requires 3 hosts with at least one block
device on each host that can be dedicated for sole use by Ceph. However, with
tweaks to the Ceph cluster you can deploy a **healthy** cluster with a single
host and a single block device.

Requirements
============

* A minimum of 3 hosts for a vanilla deploy
* A minimum of 1 block device per host

Preparation
===========

To prepare a disk for use as a
`Ceph OSD <http://docs.ceph.com/docs/master/man/8/ceph-osd/>`_ you must add a
special partition label to the disk. This partition label is how Kolla detects
the disks to format and bootstrap. Any disk with a matching partition label
will be reformatted so use caution.

To prepare an OSD as a storage drive, execute the following operations:

::

    # <WARNING ALL DATA ON $DISK will be LOST!>
    # where $DISK is /dev/sdb or something similar
    parted $DISK -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP 1 -1

The following shows an example of using parted to configure ``/dev/sdb`` for
usage with Kolla.

::

    parted /dev/sdb -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP 1 -1
    parted /dev/sdb print
    Model: VMware, VMware Virtual S (scsi)
    Disk /dev/sdb: 10.7GB
    Sector size (logical/physical): 512B/512B
    Partition Table: gpt
    Number  Start   End     Size    File system  Name                      Flags
         1      1049kB  10.7GB  10.7GB               KOLLA_CEPH_OSD_BOOTSTRAP


Using an external journal drive
-------------------------------

The steps documented above created a journal partition of 5 GByte
and a data partition with the remaining storage capacity on the same tagged
drive.

It is a common practice to place the journal of an OSD on a separate
journal drive. This section documents how to use an external journal drive.

Prepare the storage drive in the same way as documented above:

::

    # <WARNING ALL DATA ON $DISK will be LOST!>
    # where $DISK is /dev/sdb or something similar
    parted $DISK -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_FOO 1 -1

To prepare the journal external drive execute the following command:

::

    # <WARNING ALL DATA ON $DISK will be LOST!>
    # where $DISK is /dev/sdc or something similar
    parted $DISK -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_FOO_J 1 -1

.. note::

   Use different suffixes (``_42``, ``_FOO``, ``_FOO42``, ..) to use different external
   journal drives for different storage drives. One external journal drive can only
   be used for one storage drive.

.. note::

   The partition labels ``KOLLA_CEPH_OSD_BOOTSTRAP`` and ``KOLLA_CEPH_OSD_BOOTSTRAP_J``
   are not working when using external journal drives. It is required to use
   suffixes (``_42``, ``_FOO``, ``_FOO42``, ..). If you want to setup only one
   storage drive with one external journal drive it is also necessary to use a suffix.


Configuration
=============

Edit the [storage] group in the inventory which contains the hostname of the
hosts that have the block devices you have prepped as shown above.

::

    [storage]
    controller
    compute1


Enable Ceph in ``/etc/kolla/globals.yml``:

::

    enable_ceph: "yes"


RadosGW is optional, enable it in ``/etc/kolla/globals.yml``:

::

    enable_ceph_rgw: "yes"

RGW requires a healthy cluster in order to be successfully deployed. On initial
start up, RGW will create several pools. The first pool should be in an
operational state to proceed with the second one, and so on. So, in the case of
an **all-in-one** deployment, it is necessary to change the default number of
copies for the pools before deployment. Modify the file
``/etc/kolla/config/ceph.conf`` and add the contents::

    [global]
    osd pool default size = 1
    osd pool default min size = 1


Deployment
==========

Finally deploy the Ceph-enabled OpenStack:

::

    kolla-ansible deploy -i path/to/inventory

Using a Cache Tier
==================

An optional `cache tier <http://docs.ceph.com/docs/jewel/rados/operations/cache-tiering/>`_
can be deployed by formatting at least one cache device and enabling cache.
tiering in the globals.yml configuration file.

To prepare an OSD as a cache device, execute the following operations:

::

    # <WARNING ALL DATA ON $DISK will be LOST!>
    # where $DISK is /dev/sdb or something similar
    parted $DISK -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_CACHE_BOOTSTRAP 1 -1

Enable the Ceph cache tier in ``/etc/kolla/globals.yml``:

::

    enable_ceph: "yes"
    ceph_enable_cache: "yes"
    # Valid options are [ forward, none, writeback ]
    ceph_cache_mode: "writeback"

After this run the playbooks as you normally would. For example:

::

    kolla-ansible deploy -i path/to/inventory

Setting up an Erasure Coded Pool
================================

`Erasure code <http://docs.ceph.com/docs/jewel/rados/operations/erasure-code/>`_
is the new big thing from Ceph. Kolla has the ability to setup your Ceph pools
as erasure coded pools. Due to technical limitations with Ceph, using erasure
coded pools as OpenStack uses them requires a cache tier. Additionally, you
must make the choice to use an erasure coded pool or a replicated pool
(the default) when you initially deploy. You cannot change this without
completely removing the pool and recreating it.

To enable erasure coded pools add the following options to your
``/etc/kolla/globals.yml`` configuration file:

::

    # A requirement for using the erasure-coded pools is you must setup a cache tier
    # Valid options are [ erasure, replicated ]
    ceph_pool_type: "erasure"
    # Optionally, you can change the profile
    #ceph_erasure_profile: "k=4 m=2 ruleset-failure-domain=host"

Managing Ceph
=============

Check the Ceph status for more diagnostic information. The sample output below
indicates a healthy cluster:

::

    docker exec ceph_mon ceph -s
    cluster 5fba2fbc-551d-11e5-a8ce-01ef4c5cf93c
     health HEALTH_OK
     monmap e1: 1 mons at {controller=10.0.0.128:6789/0}
            election epoch 2, quorum 0 controller
     osdmap e18: 2 osds: 2 up, 2 in
      pgmap v27: 64 pgs, 1 pools, 0 bytes data, 0 objects
            68676 kB used, 20390 MB / 20457 MB avail
                  64 active+clean

If Ceph is run in an **all-in-one** deployment or with less than three storage
nodes, further configuration is required. It is necessary to change the default
number of copies for the pool. The following example demonstrates how to change
the number of copies for the pool to 1:

::

    docker exec ceph_mon ceph osd pool set rbd size 1

All the pools must be modified if Glance, Nova, and Cinder have been deployed.
An example of modifying the pools to have 2 copies:

::

    for p in images vms volumes backups; do docker exec ceph_mon ceph osd pool set ${p} size 2; done

If using a cache tier, these changes must be made as well:

::

    for p in images vms volumes backups; do docker exec ceph_mon ceph osd pool set ${p}-cache size 2; done

The default pool Ceph creates is named **rbd**. It is safe to remove this pool:

::

    docker exec ceph_mon ceph osd pool delete rbd rbd --yes-i-really-really-mean-it

Troubleshooting
===============

Deploy fails with 'Fetching Ceph keyrings ... No JSON object could be decoded'
------------------------------------------------------------------------------

If an initial deploy of Ceph fails, perhaps due to improper configuration or
similar, the cluster will be partially formed and will need to be reset for a
successful deploy.

In order to do this the operator should remove the `ceph_mon_config` volume
from each Ceph monitor node:

::

    ansible \
        -i ansible/inventory/multinode \
        -a 'docker volume rm ceph_mon_config' \
        ceph-mon
