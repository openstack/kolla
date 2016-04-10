===================================
Deploy Kolla images with Kubernetes
===================================

https://blueprints.launchpad.net/kolla/+spec/kolla-kubernetes

Kubernetes was evaluated by the Kolla team in the first two months of the project
and it was found to be problematic because it did not support net=host,
pid=host, and --privileged features of docker.  Since then, it has developed
these features. (https://github.com/kubernetes/kubernetes/releases/tag/v1.2.0)

Though Kolla deploys the containers using Ansible, we can leverage the current
work by using the config generation and injecting the configs into
the Kubernetes pod.


Problem description
===================

Kubernetes
- life-cycle management: service monitoring, restarting, and scaling
- upgrades: rolling and all at once upgrades

Kubernetes has services/tools that can provide service monitoring, health
checks, service scaling, and upgrades.

We can use the scheduler to assign work loads to appropriate nodes.
Kubernetes has built in health checks that will maintain the container's status.
And we can use the replication processes[1] to scale up and down our stack.

For upgrades, Kubernetes has a tool called 'deployments'[2], which will
detect when there is a config change in the container and start scaling
down the current running container and scaling up the new container. If
the new container fails, it can roll back, a nice feature containers provide
for us.  Though this is oversimplified for OpenStack, we can make use of this.


Proposed change
===============

- Add a deployment specific git repo (kolla-kubernetes) to contain the
  Kubernetes deployment code.

Bootstrapping
-------------

Kubernetes provides RestartPolicy which allows to define whether a container
should be restarted and when[3]. It may be used for bootstraping.

Another alternative is Ansible, which runs a number of scripts to setup the
database, keystone, etc..

Security impact
---------------

The deployed OpenStack’s security should not be affected by the deployment tool.
In addition, if we containerize the config data so that it can be injected into
a pod, we can leverage the selinux capabilities in the config container.

Performance Impact
------------------

Unknown


Implementation
==============

Primary Assignee(s)
-----------
  Ryan Hallisey (rhallisey)

Other contributor(s):
  Michal Rostecki (mrostecki)
  Swapnil Kulkarni (coolsvap)
  MD NADEEM (mail2nadeem92)
  Vikram Hosakote (vhosakot)
  <Please add your name here if you are getting involved in kolla-kubernetes>

Milestones
----------

Target Milestone for completion:
  unknown

Work Items
----------
1. Change start.yml files so that they can inject configs into Kubernetes pod.
2. Add support for kolla-kubernetes to kolla-cli.


Testing
=======

Functional tests will be implemented in the OpenStack check/gating system to
automatically checks that the Kubernetes deployment works for an AIO
environment.


Documentation Impact
====================
Add a quick start guide which will explain how to deploy kolla-kubernetes.
Add a develop guide on how to contribute, which also explains how the
deployment works.


References
==========

- [1] http://kubernetes.io/v1.0/docs/user-guide/managing-deployments.html
- [2] https://cloud.google.com/container-engine/docs/replicationcontrollers/
- [3] https://github.com/kubernetes/kubernetes/blob/master/docs/user-guide/pod-states.md#restartpolicy
- https://github.com/kubernetes/kubernetes
