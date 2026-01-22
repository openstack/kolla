==============
Kolla Overview
==============

.. image:: https://governance.openstack.org/tc/badges/kolla.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on


The Kolla project is a member of the OpenStack `Governance
<https://governance.openstack.org/tc/reference/projects/index.html>`__.

Kolla's mission statement is:

::

    To provide tools to create production-ready containers and
    to provide deployment tools for operating OpenStack clouds.

Kolla provides tools to create containers that can be run under either
`Docker <https://docker.com/>`__ or `Podman <https://podman.io/>`, as well as
`Ansible <https://ansible.com/>`__ playbooks to deploy OpenStack on baremetal
or virtual machine to meet Kolla's mission.

Kolla has out of the box defaults for a working basic deployment, and also
implements complete customization. This model permits operators with minimal
experience to deploy OpenStack quickly and as the operator's experience grows
modify the OpenStack configuration to suit the operator's exact requirements.

Getting Started
===============

Learn about Kolla by reading the documentation online
`Kolla <https://docs.openstack.org/kolla/latest/>`__.

Get started by reading the `Kolla Ansible Developer
Quickstart <https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html>`__.

The Kolla Repository
====================

The Kolla repository is one of four deliverables of the OpenStack Kolla
project. The four deliverables that make up the Kolla project are:

========================  ======================================================
Deliverable               Repository
========================  ======================================================
kolla                     https://opendev.org/openstack/kolla
kolla-ansible             https://opendev.org/openstack/kolla-ansible
ansible-collection-kolla  https://opendev.org/openstack/ansible-collection-kolla
kayobe                    https://opendev.org/openstack/kayobe
========================  ======================================================

The Kolla developers publish images in the Quay.io `openstack.kolla` namespace
for every tagged release. You can view the available images on `Quay.io
<https://quay.io/organization/openstack.kolla>`__.

.. warning::
   Kolla(-ansible) defaults to using these images in order to ease testing and
   demonstration setups, but they are not intended to be used beyond this.
   In particular, they do not undergo any security scrutiny. If you intend to
   deploy Kolla for production purposes, you are advised to create and curate your
   own set of images using the ``kolla`` tool.

OpenStack services
------------------

Kolla provides images to deploy the following OpenStack projects:

- `Aodh <https://docs.openstack.org/aodh/latest/>`__
- `Barbican <https://docs.openstack.org/barbican/latest/>`__
- `Bifrost <https://docs.openstack.org/bifrost/latest/>`__
- `Blazar <https://docs.openstack.org/blazar/latest/>`__
- `Ceilometer <https://docs.openstack.org/ceilometer/latest/>`__
- `Cinder <https://docs.openstack.org/cinder/latest/>`__
- `CloudKitty <https://docs.openstack.org/cloudkitty/latest/>`__
- `Cyborg <https://docs.openstack.org/cyborg/latest/>`__
- `Designate <https://docs.openstack.org/designate/latest/>`__
- `Glance <https://docs.openstack.org/glance/latest/>`__
- `Heat <https://docs.openstack.org/heat/latest/>`__
- `Horizon <https://docs.openstack.org/horizon/latest/>`__
- `Ironic <https://docs.openstack.org/ironic/latest/>`__
- `Keystone <https://docs.openstack.org/keystone/latest/>`__
- `Kuryr <https://docs.openstack.org/kuryr/latest/>`__
- `Magnum <https://docs.openstack.org/magnum/latest/>`__
- `Manila <https://docs.openstack.org/manila/latest/>`__
- `Masakari <https://docs.openstack.org/masakari/latest/>`__
- `Mistral <https://docs.openstack.org/mistral/latest/>`__
- `Neutron <https://docs.openstack.org/neutron/latest/>`__
- `Nova <https://docs.openstack.org/nova/latest/>`__
- `Octavia <https://docs.openstack.org/octavia/latest/>`__
- `Placement <https://docs.openstack.org/placement/latest/>`__
- Skyline (`APIServer <https://docs.openstack.org/skyline-apiserver/latest/>`__ and `Console <https://docs.openstack.org/skyline-console/latest/>`__)
- `Tacker <https://docs.openstack.org/tacker/latest/>`__
- `Trove <https://docs.openstack.org/trove/latest/>`__
- `Watcher <https://docs.openstack.org/watcher/latest/>`__
- `Zun <https://docs.openstack.org/zun/latest/>`__

Infrastructure components
-------------------------

Kolla provides images to deploy the following infrastructure components:

- `Collectd <https://collectd.org>`__,
  `Grafana <https://grafana.com>`__ for performance monitoring.
- `Cron <https://cron-job.org>`__ for log rotation.
- `Etcd <https://etcd.io/>`__ a distributed key value store that provides
  a reliable way to store data across a cluster of machines.
- `Fluentd <https://www.fluentd.org/>`__ as an open source data collector
  for unified logging layer.
- `Gnocchi <https://gnocchi.xyz/>`__ a time-series storage database.
- `Corosync <https://clusterlabs.org/corosync.html>`__ and
  `Pacemaker <https://clusterlabs.org/pacemaker>`__ for HAcluster.
- `HAProxy <https://www.haproxy.org/>`__ and
  `Keepalived <https://www.keepalived.org/>`__ for high availability of services
  and their endpoints.
- `MariaDB and Galera Cluster <https://mariadb.com/kb/en/library/galera-cluster/>`__
  for highly available MySQL databases.
- `Memcached <https://www.memcached.org/>`__ a distributed memory object caching system.
- MariaDB Backup A tool which provides a method of performing a hot backup of your MySQL data while the
  system is running.
- `Open vSwitch <https://www.openvswitch.org/>`__ for use with Neutron.
- `Opensearch <https://opensearch.org/>`__ to search, analyze,
  and visualize log messages.
- `Prometheus <https://prometheus.io/>`__ an open-source systems monitoring
  and alerting toolkit originally built at SoundCloud.
- `RabbitMQ <https://www.rabbitmq.com/>`__ as a broker messaging back end for
  communication between services.
- `Valkey Sentinel <https://valkey.io/topics/sentinel>`__ provides high availability for valkey
  along with collateral tasks such as monitoring, notification and acts as configuration
  provider for clients.
- `Telegraf <https://www.docs.influxdata.com/telegraf/>`__ as a plugin-driven server
  agent for collecting & reporting metrics.

Directories
===========

-  ``contrib`` - Contains sample template override files.
-  ``doc`` - Contains documentation.
-  ``docker`` - Contains jinja2 templates for the Docker build system.
-  ``etc`` - Contains a reference etc directory structure which requires
   configuration of a small number of configuration variables to build
   docker images.
-  ``kolla`` - Contains Python modules for kolla image build system.
-  ``releasenotes`` - Contains the releasenote for all added features
   in kolla.
-  ``roles`` - Contains Ansible roles used in CI.
-  ``specs`` - Contains the Kolla communities key arguments about
   architectural shifts in the code base.
-  ``tests`` - Contains functional testing tools.
-  ``tools`` - Contains tools for interacting with the kolla repository.

Getting Involved
================

Need a feature? Find a bug? Let us know! Contributions are much
appreciated and should follow the standard `Gerrit
workflow <https://docs.openstack.org/infra/manual/developers.html>`__.

-  We communicate using the #openstack-kolla irc channel.
-  File bugs, blueprints, track releases, etc on
   `Launchpad <https://launchpad.net/kolla>`__.
-  Attend weekly
   `meetings
   <https://docs.openstack.org/kolla/latest/contributor/meeting.html>`__.
-  Contribute `code <https://opendev.org/openstack/kolla>`__.

Notices
=======

Docker and the Docker logo are trademarks or registered trademarks of
Docker, Inc. in the United States and/or other countries. Docker, Inc.
and other parties may also have trademark rights in other terms used herein.
