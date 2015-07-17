Kolla Overview
==============

The Kolla project is part of the OpenStack [TripleO][] effort, focused
on deploying OpenStack services using [Docker][] containers. The initial
system [spec][] provides additional details of Kolla and the use cases
it addresses.

[TripleO]: https://wiki.openstack.org/wiki/TripleO
[Docker]: http://docker.com/
[spec]: https://github.com/stackforge/kolla/blob/master/specs/containerize-openstack.rst

Getting Started
===============

Deployment on bare metal is a complex topic which is beyond the scope of
the project at this time. An environment to simplify the deployment of a
single or multi-node Kolla cluster is required for development purposes.
As a result, a [Heat template][] has been created for deploying a Kolla
cluster to an existing OpenStack cloud.

[Heat template]: (https://github.com/stackforge/kolla/blob/master/devenv/README.md)

Docker Images
-------------

The [Docker images][] are built by the Kolla project maintainers. A detailed
process for contributing to the images can be found [here][]. Images reside
in the Docker Hub [Kollaglue repo][].

[here]: https://github.com/stackforge/kolla/blob/master/docs/image-building.md
[Docker images]: https://docs.docker.com/userguide/dockerimages/
[Kollaglue repo]: https://registry.hub.docker.com/repos/kollaglue/

The Kolla developers build images in the kollaglue namespace for the following
services:
* Glance
* Heat
* Keystone
* Mariadb
* Nova
* Rabbitmq
* Neutron
* Mongodb
* Ceilometer
* Horizon
* Zaqar
* Magnum
* Gnocchi

```
$ sudo docker search kollaglue
```
A list of the upstream built docker images will be shown.

Directories
===========

* docker - contains artifacts for use with docker build to build appropriate
  images
* compose - contains the docker-compose files defining the container sets
* tools - contains different tools for interacting with Kolla
* devenv - A collection of tools and resources for managing a Kolla
  development environment.

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

Check out who's [contributing][].

[contributing]: https://github.com/stackforge/kolla/graphs/contributors
