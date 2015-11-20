Ceph in Kolla
=============

Requirements
------------

Using Ceph requires at least two physical disks across the OpenStack deployment to operate correctly.

Preparation and Deployment
--------------------------

For the disks used for Ceph, execute the following operations:


::

    <WARNING ALL DATA ON $DISK will be LOST!>
    parted  $DISK -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP 1 -1
    where $DISK == /dev/sdb or something similar

The following shows an example of using parted to configure /dev/sdb for usage with Kolla.

::

    parted /dev/sdb -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP 1 -1
    parted /dev/sdb print
    Model: VMware, VMware Virtual S (scsi)
    Disk /dev/sdb: 10.7GB
    Sector size (logical/physical): 512B/512B
    Partition Table: gpt
    Number  Start   End     Size    File system  Name                      Flags
         1      1049kB  10.7GB  10.7GB               KOLLA_CEPH_OSD_BOOTSTRAP


Edit the [storage] group in the inventory which contains the hostname(or IP) of the Ceph-OSD hosts
which have the above disks. Note: ssh authentication is required for Ceph, even in all-in-one.
(TODO(CBR09): insert link to bug around this if there is one). The following shows an example
of two Ceph-OSD hosts which using one disk of the controller node and one disk of compute1.

::

    file: ansible/inventory/multinode
    ...
    [storage]
    controller
    compute1
    ...

For AIO:

::

    file: ansible/inventory/multinode
    ...
    [storage]
    all-in-one
    ...


Enable Ceph in /etc/kolla/globals.yml (Ceph is disabled by default):

::

    file: /etc/kolla/globals.yml
    ....
    enable_ceph: "yes"
    ....

Finally deploy the Ceph-enabled OpenStack:

::

    tools/kolla-ansible deploy -i ansible/inventory/multinode

Debugging Ceph
--------------

If Ceph is run in an all-in-one deployment or with less than three storage nodes, further
configuration is required. It is necessary to change the default number of copies for the pool.
The following example demonstrates how to change the number of copies for the pool:

If the deployment includes two Ceph-OSD hosts as mentioned above, set the pool to 2.

::

    docker exec ceph_mon ceph osd pool set rbd size 2 (default only have rdb pool)

For AIO:

::

    docker exec ceph_mon ceph osd pool set rbd size 1 (default only have rdb pool)

If Glance, Nova, and cinder have been deployed, all pools have to be modified.
An example of modifying the pools:

::

    for p in images vms volumes backups rbd; do docker exec ceph_mon ceph osd pool set $p size 2; done


For AIO:

::

    for p in images vms volumes backups rbd; do docker exec ceph_mon ceph osd pool set $p size 1; done

After making this change, it is mandatory to restart all Ceph osd containers.

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
