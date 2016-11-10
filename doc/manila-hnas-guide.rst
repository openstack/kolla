.. _manila-hnas-guide:

========================================================
Hitachi NAS Platform File Services Driver for OpenStack
========================================================

Overview
========
The Hitachi NAS Platform File Services Driver for OpenStack
provides NFS Shared File Systems to OpenStack.


Requirements
------------
- Hitachi NAS Platform Models 3080, 3090, 4040, 4060, 4080, and 4100.

- HNAS/SMU software version is 12.2 or higher.

- HNAS configuration and management utilities to create a storage pool (span)
  and an EVS.

  -  GUI (SMU).

  -  SSC CLI.


Supported shared filesystems and operations
------------------------------------------
The driver supports CIFS and NFS shares.

The following operations are supported:

- Create a share.

- Delete a share.

- Allow share access.

- Deny share access.

- Create a snapshot.

- Delete a snapshot.

- Create a share from a snapshot.

- Extend a share.

- Shrink a share.

- Manage a share.

- Unmanage a share.


Preparation and Deployment
==========================

.. note::

    The manila-share node only requires the HNAS EVS data interface if you
    plan to use share migration.

.. important ::

   It is mandatory that HNAS management interface is reachable from the
   Shared File System node through the admin network, while the selected
   EVS data interface is reachable from OpenStack Cloud, such as through
   Neutron flat networking.


Configuration on Kolla deployment
---------------------------------

Enable Shared File Systems service and HNAS driver in ``/etc/kolla/globals.yml``

.. code-block:: console

    enable_manila: "yes"
    enable_manila_backend_hnas: "yes"

Configure the OpenStack networking so it can reach HNAS Management
interface and HNAS EVS Data interface.

To configure two physical networks, physnet1 and physnet2, with
ports eth1 and eth2 associated respectively:

In ``/etc/kolla/globals.yml`` set:

.. code-block:: console

    neutron_bridge_name: "br-ex,br-ex2"
    neutron_external_interface: "eth1,eth2"

.. note::

     eth1: Neutron external interface.
     eth2: HNAS EVS data interface.


HNAS back end configuration
--------------------------

In ``/etc/kolla/globals.yml`` uncomment and set:

.. code-block:: console

    hnas_ip: "172.24.44.15"
    hnas_user: "supervisor"
    hnas_password: "supervisor"
    hnas_evs_id: "1"
    hnas_evs_ip: "10.0.1.20"
    hnas_file_system_name: "FS-Manila"


Configuration on HNAS
---------------------

Create the data HNAS network in Kolla OpenStack:

List the available tenants:

.. code-block:: console

    $ openstack project list

Create a network to the given tenant (service), providing the tenant ID,
a name for the network, the name of the physical network over which the
virtual network is implemented, and the type of the physical mechanism by
which the virtual network is implemented:

.. code-block:: console

    $ neutron net-create --tenant-id <SERVICE_ID> hnas_network \
    --provider:physical_network=physnet2 --provider:network_type=flat

*Optional* - List available networks:

.. code-block:: console

    $ neutron net-list

Create a subnet to the same tenant (service), the gateway IP of this subnet,
a name for the subnet, the network ID created before, and the CIDR of
subnet:

.. code-block:: console

    $ neutron subnet-create --tenant-id <SERVICE_ID> --gateway <GATEWAY> \
    --name hnas_subnet <NETWORK_ID> <SUBNET_CIDR>

*Optional* - List available subnets:

.. code-block:: console

    $ neutron subnet-list

Add the subnet interface to a router, providing the router ID and subnet
ID created before:

.. code-block:: console

    $ neutron router-interface-add <ROUTER_ID> <SUBNET_ID>

Create a file system on HNAS. See the `Hitachi HNAS reference <http://www.hds.com/assets/pdf/hus-file-module-file-services-administration-guide.pdf>`_.

.. important ::

    Make sure that the filesystem is not created as a replication target.
    Refer official HNAS administration guide.

Prepare the HNAS EVS network.

Create a route in HNAS to the tenant network:

.. code-block:: console

    $ console-context --evs <EVS_ID_IN_USE> route-net-add --gateway <FLAT_NETWORK_GATEWAY> \
    <TENANT_PRIVATE_NETWORK>

.. important ::

    Make sure multi-tenancy is enabled and routes are configured per EVS.

.. code-block:: console

    $ console-context --evs 3 route-net-add --gateway 192.168.1.1 \
    10.0.0.0/24


Create a share
==============

Create a default share type before running manila-share service:

.. code-block:: console

    $ manila type-create default_share_hitachi False

    +--------------------------------------+-----------------------+------------+------------+--------------------------------------+-------------------------+
    | ID                                   | Name                  | visibility | is_default | required_extra_specs                 | optional_extra_specs    |
    +--------------------------------------+-----------------------+------------+------------+--------------------------------------+-------------------------+
    | 3e54c8a2-1e50-455e-89a0-96bb52876c35 | default_share_hitachi | public     | -          | driver_handles_share_servers : False | snapshot_support : True |
    +--------------------------------------+-----------------------+------------+------------+--------------------------------------+-------------------------+

Create a NFS share using the HNAS back end:

.. code-block:: console

    manila create NFS 1 \
        --name mysharehnas \
        --description "My Manila share" \
        --share-type default_share_hitachi

Verify Operation

.. code-block:: console

    $ manila list

    +--------------------------------------+----------------+------+-------------+-----------+-----------+-----------------------+-------------------------+-------------------+
    | ID                                   | Name           | Size | Share Proto | Status    | Is Public | Share Type Name       | Host                    | Availability Zone |
    +--------------------------------------+----------------+------+-------------+-----------+-----------+-----------------------+-------------------------+-------------------+
    | 721c0a6d-eea6-41af-8c10-72cd98985203 | mysharehnas    | 1    | NFS         | available | False     | default_share_hitachi | control@hnas1#HNAS1     | nova              |
    +--------------------------------------+----------------+------+-------------+-----------+-----------+-----------------------+-------------------------+-------------------+

.. code-block:: console

    $ manila show mysharehnas

    +-----------------------------+-----------------------------------------------------------------+
    | Property                    | Value                                                           |
    +-----------------------------+-----------------------------------------------------------------+
    | status                      | available                                                       |
    | share_type_name             | default_share_hitachi                                           |
    | description                 | My Manila share                                                 |
    | availability_zone           | nova                                                            |
    | share_network_id            | None                                                            |
    | export_locations            |                                                                 |
    |                             | path = 172.24.53.1:/shares/45ed6670-688b-4cf0-bfe7-34956648fb84 |
    |                             | preferred = False                                               |
    |                             | is_admin_only = False                                           |
    |                             | id = e81e716f-f1bd-47b2-8a56-2c2f9e33a98e                       |
    |                             | share_instance_id = 45ed6670-688b-4cf0-bfe7-34956648fb84        |
    | share_server_id             | None                                                            |
    | host                        | control@hnas1#HNAS1                                             |
    | access_rules_status         | active                                                          |
    | snapshot_id                 | None                                                            |
    | is_public                   | False                                                           |
    | task_state                  | None                                                            |
    | snapshot_support            | True                                                            |
    | id                          | 721c0a6d-eea6-41af-8c10-72cd98985203                            |
    | size                        | 1                                                               |
    | user_id                     | ba7f6d543713488786b4b8cb093e7873                                |
    | name                        | mysharehnas                                                     |
    | share_type                  | 3e54c8a2-1e50-455e-89a0-96bb52876c35                            |
    | has_replicas                | False                                                           |
    | replication_type            | None                                                            |
    | created_at                  | 2016-10-14T14:50:47.000000                                      |
    | share_proto                 | NFS                                                             |
    | consistency_group_id        | None                                                            |
    | source_cgsnapshot_member_id | None                                                            |
    | project_id                  | c3810d8bcc3346d0bdc8100b09abbbf1                                |
    | metadata                    | {}                                                              |
    +-----------------------------+-----------------------------------------------------------------+


For more information about how to manage shares, see the
`OpenStack User Guide
<http://docs.openstack.org/user-guide/index.html>`__.

For more information about how HNAS driver works, see
`Hitachi NAS Platform File Services Driver for OpenStack
<http://docs.openstack.org/developer/manila/devref/hitachi_hnas_driver.html>`__.
