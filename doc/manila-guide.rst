.. _manila-guide:

===============
Manila in Kolla
===============

Overview
========
Currently, Kolla can deploy following manila services:

* manila-api
* manila-scheduler
* manila-share

The OpenStack Shared File Systems service (Manila) provides file storage to a
virtual machine. The Shared File Systems service provides an infrastructure
for managing and provisioning of file shares. The service also enables
management of share types as well as share snapshots if a driver supports
them.

Important
=========

For simplicity, this guide describes configuring the Shared File Systems
service to use the ``generic`` back end with the driver handles share
server mode (DHSS) enabled that uses Compute (nova), Networking (neutron)
and Block storage (cinder) services.
Networking service configuration requires the capability of networks being
attached to a public router in order to create shared networks.

Before you proceed, ensure that Compute, Networking and Block storage
services are properly working.

Preparation and Deployment
==========================

Cinder and Ceph are required, enable it in ``/etc/kolla/globals.yml``:

.. code-block:: console

    enable_cinder: "yes"
    enable_ceph: "yes"

Enable Manila and generic back end in ``/etc/kolla/globals.yml``:

.. code-block:: console

    enable_manila: "yes"
    enable_manila_backend_generic: "yes"

By default Manila uses instance flavor id 100 for its file systems. For Manila
to work, either create a new nova flavor with id 100 (use *nova flavor-create*)
or change *service_instance_flavor_id* to use one of the default nova flavor
ids.
Ex: *service_instance_flavor_id = 2* to use nova default flavor ``m1.small``.

Create or modify the file ``/etc/kolla/config/manila-share.conf`` and add the
contents:

.. code-block:: console

    [generic]
    service_instance_flavor_id = 2

Verify Operation
================

Verify operation of the Shared File Systems service. List service components
to verify successful launch of each process:

.. code-block:: console

    # manila service-list
    +------------------+----------------+------+---------+-------+----------------------------+-----------------+
    |      Binary      |    Host        | Zone |  Status | State |         Updated_at         | Disabled Reason |
    +------------------+----------------+------+---------+-------+----------------------------+-----------------+
    | manila-scheduler | controller     | nova | enabled |   up  | 2014-10-18T01:30:54.000000 |       None      |
    | manila-share     | share1@generic | nova | enabled |   up  | 2014-10-18T01:30:57.000000 |       None      |
    +------------------+----------------+------+---------+-------+----------------------------+-----------------+

Launch an Instance
==================

Before being able to create a share, the manila with the generic driver and the
DHSS mode enabled requires the definition of at least an image, a network and a
share-network for being used to create a share server. For that back end
configuration, the share server is an instance where NFS/CIFS shares are
served.

Determine the configuration of the share server
===============================================

Create a default share type before running manila-share service:

.. code-block:: console

    # manila type-create default_share_type True
    +--------------------------------------+--------------------+------------+------------+-------------------------------------+-------------------------+
    | ID                                   | Name               | Visibility | is_default | required_extra_specs                | optional_extra_specs    |
    +--------------------------------------+--------------------+------------+------------+-------------------------------------+-------------------------+
    | 8a35da28-0f74-490d-afff-23664ecd4f01 | default_share_type | public     | -          | driver_handles_share_servers : True | snapshot_support : True |
    +--------------------------------------+--------------------+------------+------------+-------------------------------------+-------------------------+

Create a manila share server image to the Image service:

.. code-block:: console

    # wget http://tarballs.openstack.org/manila-image-elements/images/manila-service-image-master.qcow2
    # glance image-create --name "manila-service-image" \
      --file manila-service-image-master.qcow2 \
      --disk-format qcow2 --container-format bare \
      --visibility public --progress
    [=============================>] 100%
    +------------------+--------------------------------------+
    | Property         | Value                                |
    +------------------+--------------------------------------+
    | checksum         | 48a08e746cf0986e2bc32040a9183445     |
    | container_format | bare                                 |
    | created_at       | 2016-01-26T19:52:24Z                 |
    | disk_format      | qcow2                                |
    | id               | 1fc7f29e-8fe6-44ef-9c3c-15217e83997c |
    | min_disk         | 0                                    |
    | min_ram          | 0                                    |
    | name             | manila-service-image                 |
    | owner            | e2c965830ecc4162a002bf16ddc91ab7     |
    | protected        | False                                |
    | size             | 306577408                            |
    | status           | active                               |
    | tags             | []                                   |
    | updated_at       | 2016-01-26T19:52:28Z                 |
    | virtual_size     | None                                 |
    | visibility       | public                               |
    +------------------+--------------------------------------+

List available networks to get id and subnets of the private network:

.. code-block:: console

    +--------------------------------------+---------+----------------------------------------------------+
    | id                                   | name    | subnets                                            |
    +--------------------------------------+---------+----------------------------------------------------+
    | 0e62efcd-8cee-46c7-b163-d8df05c3c5ad | public  | 5cc70da8-4ee7-4565-be53-b9c011fca011 10.3.31.0/24  |
    | 7c6f9b37-76b4-463e-98d8-27e5686ed083 | private | 3482f524-8bff-4871-80d4-5774c2730728 172.16.1.0/24 |
    +--------------------------------------+---------+----------------------------------------------------+

Create a shared network

.. code-block:: console

    # manila share-network-create --name demo-share-network1 \
    --neutron-net-id PRIVATE_NETWORK_ID \
    --neutron-subnet-id PRIVATE_NETWORK_SUBNET_ID
    +-------------------+--------------------------------------+
    | Property          | Value                                |
    +-------------------+--------------------------------------+
    | name              | demo-share-network1                  |
    | segmentation_id   | None                                 |
    | created_at        | 2016-01-26T20:03:41.877838           |
    | neutron_subnet_id | 3482f524-8bff-4871-80d4-5774c2730728 |
    | updated_at        | None                                 |
    | network_type      | None                                 |
    | neutron_net_id    | 7c6f9b37-76b4-463e-98d8-27e5686ed083 |
    | ip_version        | None                                 |
    | nova_net_id       | None                                 |
    | cidr              | None                                 |
    | project_id        | e2c965830ecc4162a002bf16ddc91ab7     |
    | id                | 58b2f0e6-5509-4830-af9c-97f525a31b14 |
    | description       | None                                 |
    +-------------------+--------------------------------------+

Create a flavor (**Required** if you not defined *manila_instance_flavor_id* in
``/etc/kolla/config/manila-share.conf`` file)

.. code-block:: console

    # nova flavor-create manila-service-flavor 100 128 0 1

Create a share
==============

Create a NFS share using the share network:

.. code-block:: console

    # manila create NFS 1 --name demo-share1 --share-network demo-share-network1
    +-----------------------------+--------------------------------------+
    | Property                    | Value                                |
    +-----------------------------+--------------------------------------+
    | status                      | None                                 |
    | share_type_name             | None                                 |
    | description                 | None                                 |
    | availability_zone           | None                                 |
    | share_network_id            | None                                 |
    | export_locations            | []                                   |
    | host                        | None                                 |
    | snapshot_id                 | None                                 |
    | is_public                   | False                                |
    | task_state                  | None                                 |
    | snapshot_support            | True                                 |
    | id                          | 016ca18f-bdd5-48e1-88c0-782e4c1aa28c |
    | size                        | 1                                    |
    | name                        | demo-share1                          |
    | share_type                  | None                                 |
    | created_at                  | 2016-01-26T20:08:50.502877           |
    | export_location             | None                                 |
    | share_proto                 | NFS                                  |
    | consistency_group_id        | None                                 |
    | source_cgsnapshot_member_id | None                                 |
    | project_id                  | 48e8c35b2ac6495d86d4be61658975e7     |
    | metadata                    | {}                                   |
    +-----------------------------+--------------------------------------+

After some time, the share status should change from ``creating``
to ``available``:

.. code-block:: console

    # manila list
    +--------------------------------------+-------------+------+-------------+-----------+-----------+--------------------------------------+-----------------------------+-------------------+
    | ID                                   | Name        | Size | Share Proto | Status    | Is Public | Share Type Name                      | Host                        | Availability Zone |
    +--------------------------------------+-------------+------+-------------+-----------+-----------+--------------------------------------+-----------------------------+-------------------+
    | e1e06b14-ba17-48d4-9e0b-ca4d59823166 | demo-share1 | 1    | NFS         | available | False     | default_share_type                   | share1@generic#GENERIC      | nova              |
    +--------------------------------------+-------------+------+-------------+-----------+-----------+--------------------------------------+-----------------------------+-------------------+

Configure user access to the new share before attempting to mount it via the
network:

.. code-block:: console

    # manila access-allow demo-share1 ip INSTANCE_PRIVATE_NETWORK_IP

Mount the share from an instance
================================

Get export location from share

.. code-block:: console

    # manila show demo-share1
    +-----------------------------+----------------------------------------------------------------------+
    | Property                    | Value                                                                |
    +-----------------------------+----------------------------------------------------------------------+
    | status                      | available                                                            |
    | share_type_name             | default_share_type                                                   |
    | description                 | None                                                                 |
    | availability_zone           | nova                                                                 |
    | share_network_id            | fa07a8c3-598d-47b5-8ae2-120248ec837f                                 |
    | export_locations            |                                                                      |
    |                             | path = 10.254.0.3:/shares/share-422dc546-8f37-472b-ac3c-d23fe410d1b6 |
    |                             | preferred = False                                                    |
    |                             | is_admin_only = False                                                |
    |                             | id = 5894734d-8d9a-49e4-b53e-7154c9ce0882                            |
    |                             | share_instance_id = 422dc546-8f37-472b-ac3c-d23fe410d1b6             |
    | share_server_id             | 4782feef-61c8-4ffb-8d95-69fbcc380a52                                 |
    | host                        | share1@generic#GENERIC                                               |
    | access_rules_status         | active                                                               |
    | snapshot_id                 | None                                                                 |
    | is_public                   | False                                                                |
    | task_state                  | None                                                                 |
    | snapshot_support            | True                                                                 |
    | id                          | e1e06b14-ba17-48d4-9e0b-ca4d59823166                                 |
    | size                        | 1                                                                    |
    | name                        | demo-share1                                                          |
    | share_type                  | 6e1e803f-1c37-4660-a65a-c1f2b54b6e17                                 |
    | has_replicas                | False                                                                |
    | replication_type            | None                                                                 |
    | created_at                  | 2016-03-15T18:59:12.000000                                           |
    | share_proto                 | NFS                                                                  |
    | consistency_group_id        | None                                                                 |
    | source_cgsnapshot_member_id | None                                                                 |
    | project_id                  | 9dc02df0f2494286ba0252b3c81c01d0                                     |
    | metadata                    | {}                                                                   |
    +-----------------------------+----------------------------------------------------------------------+


Create a folder where the mount will be placed:

.. code-block:: console

    # mkdir ~/test_folder

Mount the NFS share in the instance using the export location of the share:

.. code-block:: console

    # mount -v 10.254.0.3:/shares/share-422dc546-8f37-472b-ac3c-d23fe410d1b6 ~/test_folder

Share Migration
===============

As administrator, you can migrate a share with its data from one location to
another in a manner that is transparent to users and workloads. You can use
manila client commands to complete a share migration.

For share migration, is needed modify ``manila.conf`` and set a ip in the same
provider network for ``data_node_access_ip``.

Modify the file ``/etc/kolla/config/manila.conf`` and add the contents:

.. code-block:: console

    [DEFAULT]
    data_node_access_ip = 10.10.10.199


.. note::

    Share migration requires have more than one back end configured.
    `Configure multiple back ends
    <http://docs.openstack.org/developer/kolla/manila-hnas-guide.html#configure-multiple-back-ends>`__.

Use the manila migration command, as shown in the following example:

.. code-block:: console

     manila migration-start --preserve-metadata True|False \
      --writable True|False --force_host_assisted_migration True|False \
      --new_share_type share_type --new_share_network share_network \
      shareID destinationHost

- ``--force-host-copy``: Forces the generic host-based migration mechanism and
  bypasses any driver optimizations.
- ``destinationHost``: Is in this format ``host#pool`` which includes
  destination host and pool.
- ``--writable`` and ``--preserve-metadata``: Are only for driver assisted.
- ``--new_share_network``: Only if driver supports shared network.
- ``--new_share_type``: Choose share type compatible with destinationHost.

Checking share migration progress
---------------------------------

Use the ``manila migration-get-progress shareID`` command to check progress.

.. code-block:: console

     manila migration-get-progress demo-share1
     +----------------+-----------------------+
     | Property       | Value                 |
     +----------------+-----------------------+
     | task_state     | data_copying_starting |
     | total_progress | 0                     |
     +----------------+-----------------------+

     manila migration-get-progress demo-share1
     +----------------+-------------------------+
     | Property       | Value                   |
     +----------------+-------------------------+
     | task_state     | data_copying_completing |
     | total_progress | 100                     |
     +----------------+-------------------------+

Use the ``manila migration-complete shareID`` command to complete share
migration process

For more information about how to manage shares, see the
`OpenStack User Guide
<http://docs.openstack.org/user-guide/index.html>`__.
