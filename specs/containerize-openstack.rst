..
   This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================
Containerize OpenStack
======================

When upgrading or downgrading OpenStack, it is possible to use package based
management or image-based management.  Containerizing OpenStack is meant to
optimize image-based management of OpenStack.  Containerizing OpenStack
solves a manageability and availability problem with the current state of the
art deployment systems in OpenStack.

Problem description
===================

Current state of the art deployment systems use either image based or package
based upgrade.

Image based upgrades are utilized by TripleO.  When TripleO updates a system,
it creates an image of the entire disk and deploys that rather than just the
parts that compose the OpenStack deployment.  This results in significant
loss of availability.  Further running VMs are shut down in the imaging
process.  However, image based systems offer atomicity, because all related
software for a service is updated in one atomic action by reimaging the system.

Other systems use package based upgrade.  Package based upgrades suffer from
a non-atomic nature.  An update may update 1 or more RPM packages.  The update
process could fail for any number of reasons, and there is no way to back
out the existing changes.  Typically in an OpenStack deployment it is
desirable to update a service that does one thing including it's dependencies
as an atomic unit.  Package based upgrades do not offer atomicity.

To solve this problem, containers can be used to provide an image-based update
approach which offers atomic upgrade of a running system with minimal
interruption in service.  A rough prototype of compute upgrade [1] shows
approximately a 10 second window of unavailability during a software update.
The prototype keeps virtual machines running without interruption.

Use cases
---------
1. Upgrade or rollback OpenStack deployments atomically.  End-user wants to
   change the running software versions in her system to deploy a new upstream
   release without interrupting service for significant periods.
2. Upgrade OpenStack based by component.  End-user wants to upgrade her system
   in fine-grained chunks to limit damage from a failed upgrade.
3. Rollback OpenStack based by component.  End-user experienced a failed
   upgrade and wishes to rollback to the last known good working version.


Proposed change
===============
An OpenStack deployment based on containers are represented in a tree structure
with each node representing a container set, and each leaf representing a
container.

The full properties of a container set:

* A container set is composed of one or more container subsets or one or more
  individual containers
* A container set provides a single logical service
* A container set is managed as a unit during startup, shutdown, and version
* Each container set is launched together as one unit
* A container set with subsets is launched as one unit including all subsets
* A container set is not atomically managed
* A container set provides appropriate hooks for high availability monitoring

The full properties of a container:

* A container is atomically upgraded or rolled back
* A container includes a monotonically increasing generation number to identify
  the container's age in comparison with other containers
* A container has a single responsibility
* A container may be super-privileged when it needs significant access to the
  host including:

  * the network namespace of the host
  * The UUID namespace of the host
  * The IPC namespace of the host
  * Filesystem sharing of the host for persistent storage

* A container may lack any privileges when it does not require significant
  access to the host.
* A container should include a check function for evaluating its own health.
* A container will include proper PID 1 handling for reaping exited child
  processes.

The top level container sets are composed of:

* database control
* messaging control
* high availability control
* OpenStack interface
* OpenStack control
* OpenStack compute operation
* OpenStack network operation
* OpenStack storage operation

The various container sets are composed in more detail as follows:

* Database control

  * galera
  * mariadb
  * mongodb

* Messaging control

  * rabbitmq

* High availability control

  * HAProxy
  * keepalived

* OpenStack interface

  * keystone
  * glance-api
  * nova-api
  * ceilometer-api
  * heat-api

* OpenStack control

  * glance-controller

    * glance-registry

  * nova-controller

    * nova-conductor
    * nova-scheduler
    * metadata-service

  * cinder-controller
  * neutron-controller

    * neutron-server

  * ceilometer-controller

    * ceilometer-alarm
    * ceilometer-base
    * ceilometer-central
    * ceilometer-collector
    * ceilometer-notification

  * heat-controller

    * heat-engine

* OpenStack compute operation

  * nova-compute
  * nova-libvirt
  * neutron-agents-linux-bridge
  * neutron-agents-ovs

* OpenStack network operation

  * dhcp-agent
  * l3-agent
  * metadata-agent
  * lbaas-agent
  * fwaas-agent

* OpenStack storage operation

  * Cinder
  * Swift

    * swift-account
    * swift-base
    * swift-container
    * swift-object
    * swift-proxy-server

In order to achieve the desired results, we plan to permit super-privileged
containers.  A super-privileged container is defined as any container launched
with the --privileged=true flag to docker that:

* bind-mounts specific security-crucial host operating system directories
  with -v.  This includes nearly all directories in the filesystem except for
  leaf directories with no other host operating system use.
* shares any namespace with the --ipc=host, --pid=host, or --net=host flags

We will not use the Docker EXPOSE operation since all containers will use
--net=host.  One motive for using --net=host is it is inherently simpler.
A different motive for not using EXPOSE is the 20 microsecond penalty
applied to every packet forwarded and returned by docker-proxy.
If EXPOSE functionality is desired, it can be added back by
referencing the default list of OpenStack ports to each Dockerfile:

    http://docs.openstack.org/trunk/config-reference/content/firewalls-default-ports.html

We will use the docker flag --restart=always to provide some measure of
high availability for the individual containers and ensure they operate
correctly as currently designed.

A host tool will run and monitor the container's built-in check script via
docker exec to validate the container is operational on a pre-configured timer.
If the container does not pass its healthcheck operation, it should be
restarted.

Integration of metadata with fig or a similar single node Docker orchestration
tool will be implemented.  Even though fig  executes on a single node, the
containers will be designed to run multi-node and the deploy tool should take
some form of information to allow it to operate multi-node.  The deploy tool
should take a set of key/value pairs as inputs and convert them into inputs
into the environment passed to Docker.  These key/value pairs could be a file
or environment variables.  We will not offer integration with multi-node
scheduling or orchestration tools, but instead expect our consumers to manage
each bare metal machine using our fig or similar in nature tool integration.

Any contributions from the community of the required metadata to run these
containers using a multi-node orchestration tool will be warmly received but
generally won't be maintained by the core team.

The technique for launching the deploy script is not handled by Kolla.  This
is a problem for a higher level deployment tool such as TripleO or Fuel to
tackle.

Logs from the individual containers will be retrievable in some consistent way.

Security impact
---------------

Container usage with super-privileged mode may possibly impact security.  For
example, when using --net=host mode and bind-mounting /run which is necessary
for a compute node, it is possible that a compute breakout could corrupt the
host operating system.

To mitigate security concerns, solutions such as SELinux and AppArmor should
be used where appropriate to contain the security privileges of the containers.

Performance Impact
------------------

The upgrade or downgrade process changes from a multi-hour outage to a 10
second outage across the system.

Implementation
==============


Assignee(s)
-----------

Primary assignee:

kolla maintainers

Work Items
----------

1. Container Sets
2. Containers
3. A minimal proof of concept single-node fig deployment integration
4. A minimal proof of concept fig healthchecking integration

Testing
=======

Functional tests will be implemented in the OpenStack check/gating system to
automatically check that containers pass each container's functional tests
stored in the project's repositories.

Documentation Impact
====================

The documentation impact is unclear as this project is a proof of concept
with no clear delivery consumer.


References
==========

* [1] https://github.com/sdake/compute-upgrade
