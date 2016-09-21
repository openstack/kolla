.. architecture-guide:

=============================
Production architecture guide
=============================

This guide will help with configuring Kolla to suit production needs. It is
meant to answer some questions regarding basic configuration options that Kolla
requires. This document also contains other useful pointers.

Node types and services running on them
=======================================

A basic Kolla inventory consists of several types of nodes, known in Ansible as
``groups``.

* Controller - This is the cloud controller node. It hosts control services like
  APIs and databases. This group should have odd number of nodes for quorum.

* Network - This is the network node. It will host Neutron agents along with
  haproxy / keepalived. These nodes will have a floating ip defined in
  ``Kolla_internal_vip_address``.

* Compute - These are servers for compute services. This is where guest VMs
  live.

* Storage - Storage servers, for cinder-volume, LVM or ceph-osd.

Network configuration
=====================

.. _interface-configuration:

Interface configuration
***********************

In Kolla operators should configure following network interfaces:

* network_interface - While it is not used on it's own, this provides the
  required default for other interfaces below.

* api_interface - This interface is used for the management network. The
  management network is the network OpenStack services uses to communicate to
  each other and the databases. There are know security risks here, so it's
  recommended to make this network internal, not accessible from outside.
  Defaults to network_interface.

* kolla_external_vip_interface - This interface is public-facing one. It's
  used when you want HAProxy public endpoints to be exposed in different
  network than internal ones. It is mandatory to set this option when
  ``kolla_enable_tls_external`` is set to yes. Defaults to network_interface.

* storage_interface - This is the interface that is used by virtual machines to
  communicate to Ceph. This can be heavily utilized so it's recommended to put
  this network on 10Gig networking. Defaults to network_interface.

* cluster_interface - This is another interface used by Ceph. It's used for data
  replication. It can be heavily utilized also and if it becomes a bottleneck it
  can affect data consistency and performance of whole cluster. Defaults to
  network_interface.

* tunnel_interface - This interface is used by Neutron for vm-to-vm traffic over
  tunneled networks (like VxLan). Defaults to network_interface.

* Neutron_external_interface - This interface is required by Neutron. Neutron
  will put br-ex on it. It will be used for flat networking as well as tagged
  vlan networks. Has to be set separately.

Docker configuration
====================

Because Docker is core dependency of Kolla, proper configuration of Docker can
change the experience of Kolla significantly. Following section will highlight
several Docker configuration details relevant to Kolla operators.

Storage driver
**************

In certain distributions Docker storage driver defaults to devicemapper, which
can heavily hit performance of builds and deploys. We suggest to use btrfs or
aufs as driver. More details on which storage driver to use in
`Docker documentation <https://docs.docker.com/engine/userguide/storagedriver/selectadriver/>`_.

Volumes
*******

Kolla puts nearly all of persistent data in Docker volumes. These volumes are
created in Docker working directory, which defaults to

::

    /var/lib/docker

We recommend to ensure that this directory has enough space and is placed on
fast disk as it will affect performance of builds, deploys as well as database
commits and rabbitmq.

This becomes especially relevant when ``enable_central_logging`` and
``openstack_logging_debug`` are both set to true, as fully loaded 130 node
cluster produced 30-50GB of logs daily.
