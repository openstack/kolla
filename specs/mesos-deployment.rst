==============================
Deploy Kolla images with Mesos
==============================

https://blueprints.launchpad.net/kolla/+spec/mesos

Kolla deploys the containers using Ansible, however this is just one
way to deploy the containers. For example TripleO deploys Kolla
containers using Heat in-guest agents.

This specification defines the support for deploying Kolla containers
using Mesos and Marathon.

What is Mesos?
From (http://mesos.apache.org/) Mesos "provides efficient resource
isolation and sharing across distributed applications, or frameworks".
The software enables resource sharing in a fine-grained manner,
improving cluster utilization.

What is Marathon?
From (https://mesosphere.github.io/marathon/):
"A cluster-wide init and control system for services in cgroups or
Docker containers".

Adding Mesos/Marathon support to Kolla will enable those interested in
deploying OpenStack with Mesos to contribute to the Kolla community
in a more direct way.

Problem description
===================

The current deployment (Ansible) is done somewhat serially, meaning
that some services depend on others, and the deployment is controlled
by the command line (a user). In addition to deployment, Mesos/Marathon
provides the following features that will eventually be used:

- life-cycle management: like service monitoring, restart, scaling
  and rolling\restarts\upgrades
- constraints [1]: the Marathon scheduler will be used to more
  effectively place containers (esp. during scaling/recovery)
- integration with core infrastructure services like DNS, Load
  Balancing, Service Discovery and Service components.

In order to reuse a large amount of functionality, it would be best
to use an existing framework that provides a proven stable and
mature solution.
Given that Mesos/Marathon is used and tested at scale by many large
companies, it will give operators the confidence to adopt
OpenStack to meet any scaling requirements they need.

Marathon [2] will be used to manage the containers. Marathon is a
framework that runs on top of Mesos and it is for long running
services.

Part of this change is to start all the containers at the same time
(in parallel) so that there are as few dependencies from the
deployment tool’s point of view.  This should enable a couple of things:
- faster initial deployment
- reduce unnecessary restarts during upgrades
- make each container more self sufficient

Proposed change
===============

- Add a deployment specific git repo (kolla-mesos) to contain the
  Mesos/Marathon specific deployment code and boot strapping.
- Enhance Kolla container API (config.json) to permit loading
  of custom startup script while maintaining immutability with copy_once.
- Implement an all in one (AIO) basic OpenStack
- Implement a separate controller/compute setup similar to the Ansible one.
- Throughout add docs to assist users and contributors/reviewers.

Bootstrapping:
--------------

At first, Mesos/Marathon/Zookeeper bootstrapping will be done by
setting up docker container. Later, bootstrapping will be handled by Ironic/PXE
(the aim is to be practical and do what is easiest for the AIO).

Dependancy management
---------------------

Instead of the serialising the dependant steps, each container is
started and only actually starts the service if the requirements are
fulfilled.

These dependencies will come in the form of:

- service discovery (service X needs service Y running)
  Note: that Marathon DNS and LB can be self-configured based on service
        registry information.
  To achieve this the container also needs to register itself once
  it has started.
- checking to see if service configuration is complete
  (has keystone got the service user that is required, is the DB
   schema complete, etc..)
  Use Zookeeper to watch for these configuration steps.

One time tasks
--------------
Ansible runs a number of scripts to setup the database, keystone etc.
These can be run as a Mesos Executor (command line run in the
container of choice).

Security impact
---------------

Mesos and Marathon are mature products used by various companies in
production. The central configuration storage will require careful
security risk assessment. The deployed OpenStack’s security should not
be affected by the deployment tool.

Performance Impact
------------------

Given that the Mesos slaves are distributed and all containers will be
started in parallel, the deployment *may* be faster, though this is
not the main focus.

Alternatives
------------

Kubernetes was evaluated by the Kolla team 6 months ago and found to
not work at that time as it did not support net=host and pid=host
features of docker. Since then it has developed these features, if
Mesos/Marathon fails to produce results, then going back to kubernetes
is an option. However at the time of writing this Mesos/Marathon was
deemed to be more mature and stable.

Implementation
==============

Primary Assignee(s)
-----------
  Angus Salkeld (asalkeld)
  Kirill Proskurin (kproskurin)
  Michal Rostecki (nihilifer)

Other contributor(s):
  Harm Weites (harmw)
  Jeff Peeler (jpeeler)
  Michal Jastrzebski (inc0)
  Sam Yaple (SamYaple)
  Steven Dake (sdake)
  <Please add your name here if you are getting involved in kolla-mesos>

Milestones
----------

Target Milestone for completion:
  mitaka

Work Items
----------
1. Allow a custom startup script to run (change in Kolla)
2. Add startup scripts to kolla-mesos to read config from zookeeper
   instead of bindmounted directory. Propose oslo.config changes to
   use this method (oslo work done in parallel, initially this will be
   done in the startup script).
3. Add startup scripts for service discovery so that services only
   start once their needs are fulfilled.
   a. register a service once a service is running
   b. wait for dependent services if they are needed before starting
      a service.
   c. DNS and LB self-configuration based on service registry information
5. Add bootstrapping code to install Marathon, Zookeeper,
   Mesos master and slave.
6. Add calls to to marathon to deploy containers.
7. Add support for kolla-mesos to kolla-cli.

Testing
=======

Functional tests will be implemented in the OpenStack check/gating system to
automatically check that the Mesos/Marathon deployment works for an AIO environment.

Documentation Impact
====================
A quick start guide will be written to explain how to deploy.
A develop guide will be written on how to contribute and how the deployment works.

References
==========

- [1] https://mesosphere.github.io/marathon/docs/constraints.html
- [2] https://mesosphere.github.io/marathon/
- http://radar.oreilly.com/2015/10/swarm-v-fleet-v-kubernetes-v-mesos.html
- https://www.wehkamplabs.com/blog/2015/10/15/applying-consul-within-the-blaze-microservices-platform/
