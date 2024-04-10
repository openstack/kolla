=========================================
Allow Kolla Ceph to deploy bluestore OSDs
=========================================

https://blueprints.launchpad.net/kolla/+spec/kolla-ceph-bluestore

Kolla Ceph currently only supports filestore. In Queens release, the version of
Ceph is Luminous, and the bluestore is the default store type. See [1].

This spec suggests to allow Kolla Ceph to deploy bluestore OSDs by default, and
make the store type configurable.

Problem description
===================
In Ceph Luminous, the bluestore is the default store type when deploy Ceph. As
Kolla Ceph currently only supports filestore, so it is not aligned with Ceph
default behaviour. We should support both filestore and bluestore in Kolla
Ceph.

In Ceph bluestore, there are up to three partitions belong to one Ceph OSD,
they are used for block, block.wal and block.db. We should support to activate
the three partitions when deploy Ceph bluestore OSDs if the corresponding
labels are defined and associated with the physical devices.

Use cases
---------
1. Deploy Kolla Ceph and enable bluestore as default (the default value of
the parameter ``ceph_osd_store_type`` is ``bluestore`` in
``/etc/kolla/globals.yml``)
2. Deploy Kolla Ceph and enable filestore in the configuration file (change
the value of the parameter ``ceph_osd_store_type`` to ``filestore`` in
``/etc/kolla/globals.yml``)

Proposed change
===============

Exposing the store type
-----------------------
Define new configuration parameter ``ceph_osd_store_type`` in Kolla
configuration file ``/etc/kolla/globals.yml`` to indicate the store type used
in Kolla Ceph.

Existing Kolla Containers
-------------------------
In the existing Ceph-OSD container, the OSD store type will be handled when
start the Ceph OSD container. If any one label of block, block.wal or
block.db is defined, activate the Ceph OSD according to the configuration. If
there is no label associated with block.wal and block.db, then activate Ceph
OSD in one docker volume.

Indicate block, block.wal and block.db belonging to the same Ceph OSD according
to the partition labels, it keeps the same method used in Kolla Ceph filestore.
* ``KOLLA_CEPH_OSD_BOOSTRAP_BS_xxx`` is the block volume label of one bluestore
OSD
* ``KOLLA_CEPH_OSD_BOOSTRAP_BS_xxx_W`` is the block.wal volume label of one
bluestore OSD
* ``KOLLA_CEPH_OSD_BOOSTRAP_BS_xxx_D`` is the block.db volume label of one
bluestore OSD
Here, ``xxx`` is the suffix used to indicate the above volumes belong to the
same Ceph OSD.

Security Impact
---------------
There is no security impact introduced.

Performance Impact
------------------
There is no performance impact introduced.

Implementation
==============

Assignee(s)
-----------
  Tone Zhang (tone_zrt)

Milestones
----------
Target Milestone for completion: Rocky

Work Items
----------
1. Expose OSD store type in Kolla configuration file
2. Check disk partition labels when start Ceph-OSD container if the store
type is bluestore
3. Modify the Ceph-OSD starting script to support bluestore
4. Active block, block.wal and block.db configurable in Ceph bluestore OSD

Testing
=======
The existing gate checks will be used to ensure Ceph bluestore OSD
successful deployment.

Documentation Impact
====================
The reference page ``Ceph in Kolla`` [2] should be updated.
The page will document how to change the Ceph store type and how to deploy Ceph
bluestore OSD.

References
==========
[1] http://docs.ceph.com/docs/master/
[2] https://docs.openstack.org/kolla-ansible/latest/reference/ceph-guide.html
