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

The learn about Kolla, you can find the documentation online on
`docs.openstack.org <http://docs.openstack.org/developer/kolla/>`__.

You can get started by reading the `Developer
Quickstart <http://docs.openstack.org/developer/kolla/quickstart.html>`__.

Docker Images
-------------

The `Docker images <https://docs.docker.com/userguide/dockerimages/>`__
are built by the Kolla project maintainers. A detailed process for
contributing to the images can be found in the `image building
guide <http://docs.openstack.org/developer/kolla/image-building.html>`__.
Images reside in the Docker Hub `Kollaglue
repo <https://hub.docker.com/u/kollaglue/>`__.

The Kolla developers build images in the kollaglue namespace for the
following services for every tagged release and implement Ansible
deployment for them:

-  Ceilometer
-  Cinder
-  Glance
-  Haproxy
-  Heat
-  Horizon
-  Keepalived
-  Keystone
-  Mariadb + galera
-  Mongodb
-  Neutron (linuxbridge or neutron)
-  Nova
-  Openvswitch
-  Rabbitmq

::

    $ sudo docker search kollaglue

A list of the upstream built docker images will be shown.

Directories
===========

-  ansible - Contains Anible playbooks to deploy Kolla in Docker
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

-  We communicate using the #kolla irc channel.
-  File bugs, blueprints, track releases, etc on
   `Launchpad <https://launchpad.net/kolla>`__.
-  Attend weekly
   `meetings <https://wiki.openstack.org/wiki/Meetings/Kolla>`__.
-  Contribute `code <https://github.com/openstack/kolla>`__

Contributors
============

Check out who's `contributing
code <http://stackalytics.com/?module=kolla-group&metric=commits>`__ and
`contributing
reviews <http://stackalytics.com/?module=kolla-group&metric=marks>`__.
