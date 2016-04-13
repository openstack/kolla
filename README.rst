Kolla Overview
==============

The Kolla project is a member of the OpenStack `Big Tent
Governance <http://governance.openstack.org/reference/projects/index.html>`__.
Kolla's mission statement is:

::

    Kolla provides production-ready containers and deployment tools for
    operating OpenStack clouds.

Kolla provides `Docker <http://docker.com/>`__ containers and
`Ansible <http://ansible.com/>`__ playbooks to meet Kolla's mission.
Kolla is highly opinionated out of the box, but allows for complete
customization. This permits operators with little experience to deploy
OpenStack quickly and as experience grows modify the OpenStack
configuration to suit the operator's exact requirements.

Getting Started
===============

Learn about Kolla by reading the documentation online
`docs.openstack.org <http://docs.openstack.org/developer/kolla/>`__.

Get started by reading the `Developer
Quickstart <http://docs.openstack.org/developer/kolla/quickstart.html>`__.

Kolla provides images to deploy the following OpenStack projects:

- `Aodh <http://docs.openstack.org/developer/aodh/>`__
- `Ceilometer <http://docs.openstack.org/developer/ceilometer/>`__
- `Cinder <http://docs.openstack.org/developer/cinder/>`__
- `Designate <http://docs.openstack.org/developer/designate/>`__
- `Glance <http://docs.openstack.org/developer/glance/>`__
- `Gnocchi <http://docs.openstack.org/developer/gnocchi/>`__
- `Heat <http://docs.openstack.org/developer/heat/>`__
- `Horizon <http://docs.openstack.org/developer/horizon/>`__
- `Ironic <http://docs.openstack.org/developer/ironic/>`__
- `Keystone <http://docs.openstack.org/developer/keystone/>`__
- `Magnum <http://docs.openstack.org/developer/magnum/>`__
- `Manila <http://docs.openstack.org/developer/manila/>`__
- `Mistral <http://docs.openstack.org/developer/mistral/>`__
- `Murano <http://docs.openstack.org/developer/murano/>`__
- `Nova <http://docs.openstack.org/developer/nova/>`__
- `Neutron <http://docs.openstack.org/developer/neutron/>`__
- `Swift <http://docs.openstack.org/developer/swift/>`__
- `Tempest <http://docs.openstack.org/developer/tempest/>`__
- `Trove <http://docs.openstack.org/developer/trove/>`__
- `Zaqar <http://docs.openstack.org/developer/zaqar/>`__

As well as these infrastructure components:

- `Ceph <http://ceph.com/>`__ implementation for Cinder, Glance and Nova
- `Openvswitch <http://openvswitch.org/>`__ and Linuxbridge backends for Neutron
- `MongoDB <https://www.mongodb.org/>`__ as a database backend for Ceilometer
  and Gnocchi
- `RabbitMQ <https://www.rabbitmq.com/>`__ as a messaging backend for
  communication between services.
- `HAProxy <http://www.haproxy.org/>`__ and
  `Keepalived <http://www.keepalived.org/>`__ for high availability of services
  and their endpoints.
- `MariaDB and Galera <https://mariadb.com/kb/en/mariadb/galera-cluster/>`__ for
  highly available MySQL databases
- `Heka <http://hekad.readthedocs.org/en/>`__ A distributed and
  scalable logging system for openstack services.

Docker Images
=============

The `Docker images <https://docs.docker.com/userguide/dockerimages/>`__
are built by the Kolla project maintainers. A detailed process for
contributing to the images can be found in the `image building
guide <http://docs.openstack.org/developer/kolla/image-building.html>`__.

The Kolla developers build images in the `kollaglue` namespace for every tagged
release and implement an Ansible deployment for many but not all of them.

You can view the available images on `Docker Hub
<https://hub.docker.com/u/kollaglue/>`__ or with the Docker CLI::

    $ sudo docker search kollaglue

Directories
===========

-  ansible - Contains Ansible playbooks to deploy Kolla in Docker
   containers.
-  demos - Contains a few demos to use with Kolla.
-  dev/heat - Contains an OpenStack-Heat based development environment.
-  dev/vagrant - Contains a vagrant VirtualBox/Libvirt based development
   environment.
-  doc - Contains documentation.
-  etc - Contains a reference etc directory structure which requires
   configuration of a small number of configuration variables to achieve
   a working All-in-One (AIO) deployment.
-  docker - Contains jinja2 templates for the docker build system.
-  tools - Contains tools for interacting with Kolla.
-  specs - Contains the Kolla communities key arguments about
   architectural shifts in the code base.
-  tests - Contains functional testing tools.

Getting Involved
================

Need a feature? Find a bug? Let us know! Contributions are much
appreciated and should follow the standard `Gerrit
workflow <http://docs.openstack.org/infra/manual/developers.html>`__.

-  We communicate using the #openstack-kolla irc channel.
-  File bugs, blueprints, track releases, etc on
   `Launchpad <https://launchpad.net/kolla>`__.
-  Attend weekly
   `meetings <https://wiki.openstack.org/wiki/Meetings/Kolla>`__.
-  Contribute `code <https://github.com/openstack/kolla>`__.

Contributors
============

Check out who's `contributing
code <http://stackalytics.com/?module=kolla-group&metric=commits>`__ and
`contributing
reviews <http://stackalytics.com/?module=kolla-group&metric=marks>`__.
