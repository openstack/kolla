==============
Kolla Overview
==============

.. image:: https://governance.openstack.org/tc/badges/kolla.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on


The Kolla project is a member of the OpenStack `Big Tent
Governance <https://governance.openstack.org/tc/reference/projects/index.html>`__.

Kolla's mission statement is:

::

    To provide production-ready containers and deployment tools for operating
    OpenStack clouds.

Kolla provides `Docker <https://docker.com/>`__ containers,
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

The Kolla repository is one of three deliverables of the OpenStack Kolla
project. The three deliverables that make up the Kolla project are:

================   =========================================================
Deliverable        Repository
================   =========================================================
kolla              https://opendev.org/openstack/kolla
kolla-ansible      https://opendev.org/openstack/kolla-ansible
kayobe             https://opendev.org/openstack/kayobe
================   =========================================================

The `Docker images <https://docs.docker.com/storage/storagedriver/>`__
are built by the Kolla project maintainers. A detailed process for
contributing to the images can be found in the `image building
guide <https://docs.openstack.org/kolla/latest/admin/image-building.html>`__.

The Kolla developers build images in the `kolla` namespace for every tagged
release.

You can view the available images on `Docker Hub
<https://hub.docker.com/u/kolla/>`__ or with the Docker CLI::

    $ sudo docker search kolla

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
- `Freezer <https://docs.openstack.org/freezer/latest/>`__
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
- `Monasca <https://docs.openstack.org/monasca-api/latest/>`__
- `Murano <https://docs.openstack.org/murano/latest/>`__
- `Neutron <https://docs.openstack.org/neutron/latest/>`__
- `Nova <https://docs.openstack.org/nova/latest/>`__
- `Octavia <https://docs.openstack.org/octavia/latest/>`__
- `Sahara <https://docs.openstack.org/sahara/latest/>`__
- `Senlin <https://docs.openstack.org/senlin/latest/>`__
- Skyline (`APIServer <https://docs.openstack.org/skyline-apiserver/latest/>`__ and `Console <https://docs.openstack.org/skyline-console/latest/>`__)
- `Solum <https://docs.openstack.org/solum/latest/>`__
- `Swift <https://docs.openstack.org/swift/latest/>`__
- `Tacker <https://docs.openstack.org/tacker/latest/>`__
- `Trove <https://docs.openstack.org/trove/latest/>`__
- `Vitrage <https://docs.openstack.org/vitrage/latest/>`__
- `Watcher <https://docs.openstack.org/watcher/latest/>`__
- `Zun <https://docs.openstack.org/zun/latest/>`__

Infrastructure components
-------------------------

Kolla provides images to deploy the following infrastructure components:

- `Collectd <https://collectd.org>`__,
  `InfluxDB <https://influxdata.com/time-series-platform/influxdb/>`__, and
  `Grafana <https://grafana.com>`__ for performance monitoring.
- `Corosync <https://clusterlabs.org/corosync.html>`__ and
  `Pacemaker <https://clusterlabs.org/pacemaker>`__ for HAcluster.
- `Elasticsearch <https://www.elastic.co/de/products/elasticsearch>`__ and
  `Kibana <https://www.elastic.co/products/kibana>`__ to search, analyze,
  and visualize log messages.
- `Cron <https://cron-job.org>`__ for log rotation.
- `Etcd <https://etcd.io/>`__ a distributed key value store that provides
  a reliable way to store data across a cluster of machines.
- `Fluentd <https://www.fluentd.org/>`__ as an open source data collector
  for unified logging layer.
- `Gnocchi <https://gnocchi.xyz/>`__ a time-series storage database.
- `HAProxy <https://www.haproxy.org/>`__ and
  `Keepalived <https://www.keepalived.org/>`__ for high availability of services
  and their endpoints.
- `Kafka <https://kafka.apache.org/documentation/>`__ a distributed streaming
  platform.
- `MariaDB and Galera Cluster <https://mariadb.com/kb/en/library/galera-cluster/>`__
  for highly available MySQL databases.
- `Memcached <https://www.memcached.org/>`__ a distributed memory object caching system.
- `Open vSwitch <https://www.openvswitch.org/>`__ for use with Neutron.
- MariaDB Backup A tool which provides a method of performing a hot backup of your MySQL data while the
  system is running.
- `Prometheus <https://prometheus.io/>`__ an open-source systems monitoring
  and alerting toolkit originally built at SoundCloud.
- `Qdrouterd <https://qpid.apache.org/components/dispatch-router/index.html>`__ as a
  direct messaging back end for communication between services.
- `RabbitMQ <https://www.rabbitmq.com/>`__ as a broker messaging back end for
  communication between services.
- `Redis Sentinel <https://redis.io/topics/sentinel>`__ provides high availability for redis
  along with collateral tasks such as monitoring, notification and acts as configuration
  provider for clients.
- `Telegraf <https://www.docs.influxdata.com/telegraf/>`__ as a plugin-driven server
  agent for collecting & reporting metrics.
- `ZooKeeper <https://zookeeper.apache.org/>`__ as a centralized service for maintaining
  configuration information, naming, providing distributed synchronization, and providing
  group services.

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

Contributors
============

Check out who is `contributing
code <https://stackalytics.com/?module=kolla-group&metric=commits>`__ and
`contributing
reviews <https://stackalytics.com/?module=kolla-group&metric=marks>`__.

Notices
=======

Docker and the Docker logo are trademarks or registered trademarks of
Docker, Inc. in the United States and/or other countries. Docker, Inc.
and other parties may also have trademark rights in other terms used herein.
