Kolla Overview
==============

The Kolla project is a member of the OpenStack [Big Tent Governance][].
Kolla's mission statement is:

    Kolla provides production-ready containers and deployment tools for
    operating OpenStack clouds.

Kolla provides [Docker][] containers and [Ansible][] playbooks to meet Kolla's
mission.  Kolla is highly opinionated out of the box, but allows for complete
customization.  This permits operators with little experience to deploy
OpenStack quickly and as experience grows modify the OpenStack configuration
to suit the operator's exact requirements.

[Big Tent Governance]: http://governance.openstack.org/reference/projects/index.html
[Docker]: http://docker.com/
[Ansible]: http://ansible.com/

Getting Started
===============

Please get started by reading the [Developer Quickstart][] followed by the
[Ansible Deployment Guide][].

[Developer Quickstart]: https://github.com/stackforge/kolla/blob/master/docs/dev-quickstart.md
[Ansible Deployment guide]: https://github.com/stackforge/kolla/blob/master/docs/ansible-deployment.md]

Docker Images
-------------

The [Docker images][] are built by the Kolla project maintainers.  A detailed
process for contributing to the images can be found in the
[image building guide][]. Images reside in the Docker Hub [Kollaglue repo][].

[image building guide]: https://github.com/stackforge/kolla/blob/master/docs/image-building.md
[Docker images]: https://docs.docker.com/userguide/dockerimages/
[Kollaglue repo]: https://registry.hub.docker.com/repos/kollaglue/

The Kolla developers build images in the kollaglue namespace for the following
services for every tagged release and implement Ansible deployment for them:

* Ceilometer
* Cinder
* Glance
* Haproxy
* Heat
* Horizon
* Keepalived
* Keystone
* Mariadb + galera
* Mongodb
* Neutron (linuxbridge or neutron)
* Nova
* Openvswitch
* Rabbitmq

```
$ sudo docker search kollaglue
```
A list of the upstream built docker images will be shown.

Directories
===========

* ansible - Contains Anible playbooks to deploy Kolla in Docker containers.
* compose - Contains the docker-compose files serving as a compose reference.
  Note compose support is removed from Kolla.  These are for community members
  which want to use Kolla container content without Ansible.
* demos - Contains a few demos to use with Kolla.
* devenv - Contains an OpenStack-Heat based development environment.
* docker - Contains a normal Dockerfile based set of artifacts for building
  docker.  This is planned for removal when docker_templates is completed.
* docs - Contains documentation.
* etc - Contains a reference etc directory structure which requires
  configuration of a small number of configuration variables to achieve a
  working All-in-One (AIO) deployment.
* docker_templates - Contains jinja2 templates for the docker build system.
* tools - Contains tools for interacting with Kolla.
* specs - Contains the Kolla communities key arguments about architectural
  shifts in the code base.
* tests - Contains functional testing tools.
* vagrant - Contains a vagrant VirtualBox-based development environment.

Getting Involved
================

Need a feature? Find a bug? Let us know! Contributions are much appreciated
and should follow the standard [Gerrit workflow][].

- We communicate using the #kolla irc channel.
- File bugs, blueprints, track releases, etc on [Launchpad][].
- Attend weekly [meetings][].
- Contribute [code][]

[Gerrit workflow]: https://wiki.openstack.org/wiki/Gerrit_Workflow
[Launchpad]: https://launchpad.net/kolla
[meetings]: https://wiki.openstack.org/wiki/Meetings/Kolla
[code]: https://github.com/stackforge/kolla

Contributors
============

Check out who's [contributing code][] and [contributing reviews][].

[contributing code]: http://stackalytics.com/?module=kolla-group&metric=commits
[contributing reviews]: http://stackalytics.com/?module=kolla-group&metric=marks
