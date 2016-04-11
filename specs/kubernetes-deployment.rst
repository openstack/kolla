===================================
Deploy Kolla images with Kubernetes
===================================

https://blueprints.launchpad.net/kolla/+spec/kolla-kubernetes

Kubernetes was evaluated by the Kolla team in the first two months of the
project and it was found to be problematic because it did not support net=host,
pid=host, and --privileged features in docker.  Since then, it has developed
these features [1].

The objective is to manage the lifecycle of containerized OpenStack services by
using Kubernetes container managment tools in order to obtain the self-healing
and upgrade capabilities inherent in Kubernetes.

Problem description
===================

Kubernetes
- life-cycle management: service monitoring, HA, loadbalancing, and
  health checks
- upgrades: rolling

Kubernetes has services that provide kolla-kubernetes with service monitoring,
health checks, service scaling, and upgrades. The community can use the
scheduler and node affinity trait to assign work loads to appropriate nodes [2].
Kubernetes also has built in health checks that monitors a container's status.
Finally, kolla-kubernetes can use the replication controller to scale up and
down the stack [3].

For upgrades, Kubernetes has an object called 'deployments'[4], which detects
when a pod needs to change. It starts to scale down the current running
pods and scale up the new pods.

Use Cases
=========

- Kubernetes as an underlay for OpenStack.
- Kubernetes to handle container scheduling.
- Feedback loop when using Kubernetes health checks during deployment and
  upgrade.
- High Availability for individual containers

Proposed change
===============

- Add a deployment specific git repo (kolla-kubernetes) under the kolla
  governance that contains the Kubernetes deployment code.

Orchestration
-------------

OpenStack on Kubernetes will be orchestrated by outside tools in order to create
a production ready OpenStack environment.  The kolla-kubernetes repo is where
any deployment tool can join the community and be a part of orchestrating a
kolla-kubernetes deployment.

Service Config Management
-------------------------

Config generation will be completely decoupled from the deployment. The
containers only expect a config file to land in a specific directory in
the container in order to run.  With this decoupled model, any tool could be
used to generate config files.  The kolla-kubernetes community will evaluate
any config generation tool, but will likely use Ansible for config generation
in order to reuse existing work from the community.  This solution uses
customized Ansible and jinja2 templates to generate the config. Also, there will
be a maintained set of defaults and a global yaml file that can override the
defaults.

The config files will be injected into the kubernetes configmap and loaded into
the containers. There will be one configmap per configuration file and there can
be multiple config maps. The containers will configure themselves using the
configuration files loaded into the appropriate directories [5][6].

Bootstrapping
-------------

Bootstrapping the Kolla containers involves running a single task per service
that will initialize the databases and create the users. The bootstrapping task
will be a Kubernetes Job, which will run the task until completion then
terminate the pods [7].

Each service will have a bootstrap task so that when the operator upgrades,
the bootstrap tasks are reused to upgrade the database.  This will allow
deployment and upgrades to follow the same pipeline.

The Kolla containers will communicate with the Kubernetes API server to in order
to be self aware of if any bootstrapping processes are occuring.

Alternative bootstrap approaches:

1) Create 2 pods per OpenStack service. One pod is designed to do the
bootstrapping/db_sync while the other pod runs as the normal service. This will
require some orchestration and the bootstrap pod will need to be setup to
never restart or be replicated.

2) Use a sidecar container in the pod to handle the database sync with proper
health checking to make sure the services are coming up healthy.  The big
difference between kolla's old docker-compose solution and Kubernetes, is that
docker-compose would only restart the containers.  Kubernetes will completely
reschedule them.  Which means, removing the pod and restarting it.  The reason
this would fix that race condition failure kolla saw from docker-compose is
because glance would be rescheduled on failure allowing keystone to get a
chance to sync with the database and become active instead of constantly being
piled with glance requests.  There can also be health checks around this to help
determine order.

If kolla-kubernetes used this sidecar approach, it would regain the use of
native Kubernetes upgrades [16].

Dependencies
------------

- Kubernetes >= 1.3.0
- Docker >= 1.10.0
- Jinja2 >= 2.8.0

Kubernetes does not support dependencies between pods.  The operator will launch
all the services and use kubernetes health checks to bring the deployment to an
operational state.

With orchestration around Kubernetes, the operator can determine what tasks are
run and when the tasks are run.  This way, dependencies are handled at the
orchestration level, but they are not required because proper health checking
will bring up the cluster in a healthy state.

Upgrades
--------

Kubernetes has an object called a Deployment, where the operator defines a
desired state for the pods and the deployment will move the cluster to the
desired state when a change is detected.

Kolla-kubernetes will provide Jobs that will provide the operator with the
flexibility needed to under go a step wise upgrade.  In future releases,
kolla-kubernetes will look to Kubernetes to provide a means for operators to
plugin these jobs into a Deployment.

Reconfigure
-----------

The operator generates a new config and loads it into the Kubernetes configmap
by changing the configmap version in the service yaml file.  Then, the operator
will trigger a rolling upgrade, which will scale down old pods and bring up new
ones that will run with the updated configuration files.

There's an open issue upstream in Kubernetes where the plan is to add support
around detecting if a pod has a changed in the configmap [6].  Depending on what
the solution is, kolla-kubernetes may or may not use it.  The rolling
upgrade feature will provide kolla-kubernetes with an elegant way to handle
restarting the services.

HA Architecture
---------------

Kubernetes uses health checks to bring up the services.  Therefore,
kolla-kubernetes will use the same checks when monitoring if a service is
healthy.  When a service fails, the replication controller will be responsible
for bringing up a new container in its place [8][9].

However, Kubernetes does not cover all the HA corner cases, for instance,
fencing. But, there are some operator known practices that can be used to get
around this [10]. For example, to implement storage fencing, the operator can
use ceph backed storage [11][12]. This is an option that the community can
document in order to provide kolla-kubernetes with a production ready solution
if Kubernetes cannot.

.. note:: There is a known issue in Kubernetes with releasing volumes from a
node that disappeared from the cluster. This is expected to be fixed in the 1.3
release [13].

Persistent Storage
------------------

Kubernetes has many types of persistent storage [14]. Since Kubernetes doesn't
guarantee a pod will always be scheduled to a host, it makes node based
persistent storage unlikely, unless the community uses labels for every pod.

Persistent storage in kolla-kubernetes will come from volumes backed by
different storage offerings to provide persistent storage.  Kolla-kubernetes
will provide a default solution using Ceph RBD, that the community will use to
deploy multinode with. From there, kolla-kubernetes can add any additional
persistent storage options as well as support options for the operator to
reference an existing storage solution.

To deploy Ceph, the community will use the Ansible playbooks from Kolla to
deploy a containerized Ceph at least for the 1.0 release.  After Kubernetes
deployment matures, the community can evaluate building its own Ceph deployment
solution.

Existing external Ceph deployments will require additional documentation
to describe how to integrate them with a Kubernetes deployment.

Service Roles
-------------

At the broadest level, OpenStack can split up into two main roles, Controller
and Compute. With Kubernetes, the role definition layer changes.
Kolla-kubernetes will still need to define Compute nodes, but not Controller
nodes.  Compute nodes hold the libvirt container and the running vms.  That
service cannont migrate because the vms associated with it exist on the node.
However, the Controller role is more flexible.  The Kubernetes layer provides IP
persistence so that APIs will remain active and abstracted from the operator's
view [15]. kolla-kubernetes can direct Controller services away from the Compute
node using labels, while managing Compute services more strictly.

The Kubernetes Label field will be configurable to allow the operator to
define roles and direct where services will land.

Security impact
---------------

Kolla-Kubernetes will run the containers as non root wherever possible.
SELinux or AppArmor will be in place to limit the damage from container
breakouts.

Kubernetes is planning to adding capabilities to the pod level that will enable
the community to restrict container privileges even further [16].

Performance Impact
------------------

Since kolla-kubernetes is not using dependencies for the service deployment, the
services will take a different amount of time to start up for each deployment
because the order will always vary when the services become active.
As such, it's hard to quantify the exact performance impact other than it is
small.

Networking
----------

Kolla-kubernetes will initially use 'net=host' everywhere to get the project
going. As the project matures, 'net=host' needs to be reevaluated as to which
services will run without 'net=host' in order to gain additional functionality.
For example, controller services will float between nodes potentially landing
two of the same pods on the same node. Those pods will be listening on the same
ports in the hosts network stack, which could prevent the pods from working.

Logging & Monitoring
--------------------

To reuse Kolla's containers, kolla-kubernetes will use elastic search, heka, and
kibana as the default logging mechanism.

The community will implement centralized logging by using a 'side car' container
in the Kubernetes pod [17].  The logging service will trace the logs from the
shared volume of the running serivce and send the data to elastic search. This
solution is ideal because volumes are shared amoung the containers in a pod.

Implementation
==============

Primary Assignee(s)
-----------
  Ryan Hallisey (rhallisey)

Other contributor(s):
  kolla-core team [18]
  Alex Polvi (polvi)
  Andrew Battye
  Brandon Jozsa (v1k0d3n)
  Britt Houser (britthouser)
  Davanum Srinivas (dims)
  David Wang (dcwangmit01)
  Egor Guz (eghobo)
  Greg Herlein (gherlein)
  Hui Kang (huikang)
  Ian Main (Slower)
  Jinay Vora (jvora)
  Keith Byrne (kbyrne)
  Ken Wronkiewicz (wirehead)
  Kevin Fox (kfox1111)
  Marga Millet (fragatina)
  Marian Schwarz
  Mark Casey (mark-casey)
  Mauricio Lima (mlima)
  Md Nadeem (mail2nadeem92)
  Michael Schmidt
  Michal Rostecki (mrostecki)
  Qiu Yu (unicell)
  Rajath Agasthya (rajathagasthya)
  Rob Mason
  Sean Mooney (sean-k-mooney)
  Serguei Bezverkhi (sbezverk)
  Sidharth Surana (ssurana)
  Zdenek Janda (xdeu)
  <Please add your name here if you are getting involved in kolla-kubernetes>

Milestones
----------

Target Milestone for tech-preview code:
  Newton

Work Items
----------
1. Create kolla-kubernetes repo
2. Build yaml files for each service
3. Build a CLI to handle templated yaml files
4. Build an all in one environment
5. Drop net=host on a set of services
6. Write per service health checks
7. Write startup docs
8. Add orchestration tools around the pods
9. All in one gating
10. Convert each service to a 'Deployment'
11. Build multinode environment
12. Config generation tools
13. Multinode docs
14. Implement reconfigure by templating configmaps
15. Centralized logging
16. Implement upgrades
17. Advanced deployment docs
<Please add new work items that are worth mentioning in the spec>

Testing
=======

Functional tests will be implemented in the OpenStack check/gating system to
automatically test that the Kubernetes deployment works for an AIO
environment [19].

Documentation Impact
====================
Add a quick start guide, which explains how to deploy kolla-kubernetes.
Add a developer guide on how to contribute which also explains how the
deployment works.

References
==========

- [1] https://github.com/kubernetes/kubernetes/releases/tag/v1.2.0
- [2] http://kubernetes.io/docs/user-guide/node-selection/
- [3] http://kubernetes.io/v1.0/docs/user-guide/managing-deployments.html
- [4] https://cloud.google.com/container-engine/docs/replicationcontrollers/
- [5] https://github.com/kubernetes/kubernetes/blob/master/docs/design/configmap.md
- [6] https://github.com/kubernetes/kubernetes/issues/24957
- [7] http://kubernetes.io/docs/user-guide/jobs/
- [8] http://kubernetes.io/docs/user-guide/replication-controller/
- [9] http://kubernetes.io/docs/user-guide/replicasets/
- [10] http://kubernetes.io/docs/admin/high-availability/#master-elected-components
- [11] http://kubernetes.io/docs/user-guide/volumes/#rbd
- [12] http://docs.ceph.com/docs/master/cephfs/eviction/
- [13] https://github.com/kubernetes/kubernetes/issues/20262
- [14] http://kubernetes.io/docs/user-guide/volumes/
- [15] http://kubernetes.io/docs/user-guide/node-selection/
- [16] https://github.com/kubernetes/kubernetes/blob/master/docs/proposals/pod-security-context.md
- [17] http://blog.kubernetes.io/2015/06/the-distributed-system-toolkit-patterns.html
- [18] https://review.openstack.org/#/admin/groups/460,members
- [19] https://etherpad.openstack.org/p/kolla-newton-summit-kolla-gate-walkthru
- https://github.com/kubernetes/kubernetes
