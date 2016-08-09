..
   This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

======================
High-Availability
======================

Kolla deployments will be maturing from evaluation-level environments to
highly available and scalable environments supporting production
applications and services. The goal for Kolla HA is to provide active/active,
highly available and independently scalable OpenStack services. This spec
focuses on providing high availability within a single Kolla-based
OpenStack deployment.

Problem description
===================

OpenStack consists of several core and infrastructure services. The services
work in concert to provide a cloud computing environment. By default, the
services are single points of failure and are unable to scale beyond a single
instance.

Use cases
---------
1. Fail any one or a combination of OpenStack core and/or infrastructure
   services and the overall system continues to operate.
2. Scale any one or a combination of OpenStack core and/or infrastructure
   services without any interruption of service.

Proposed change
===============

The spec consists of the following components for providing high
availability and scalability to Kolla-based OpenStack services:

MySQL Galera: A synchronous multi-master database clustering technology
for MySQL/InnoDB databases that includes features such as:

  * Synchronous replication
  * Active/active multi-master topology
  * Read and write to any cluster node
  * True parallel replication, on row level
  * Direct client connections, native MySQL look & feel
  * No slave lag or integrity issues

**Note:** Although Galera supports an active/active multi-master topology
with multiple active writers, a few OpenStack services cause database
deadlocks in this scenario. This is because these services use the
SELECT... FOR UPDATE SQL construct, even though it's [documented][]
not to. It appears that [Nova][] has recently fixed the issue and
[Neutron][] is making progress

[documented]: https://github.com/openstack/nova/blob/da59d3228125d7e7427c0ba70180db17c597e8fb/nova/openstack/common/db/sqlalchemy/session.py#L180-196
[Nova]: http://specs.openstack.org/openstack/nova-specs/specs/kilo/approved/lock-free-quota-management.html
[Neutron]: https://bugs.launchpad.net/neutron/+bug/1364358 https://bugs.launchpad.net/neutron/+bug/1331564

Testing should be performed as part of the Galera implementation to verify
whether the recent patches address the deadlock issues. If so, multiple
active/active writers can exist within the Galera cluster. If not,then
the initial implementation should continue using the well documented
work around until the issue is completely resolved.

Several OpenStack services utilize a message queuing system to send and
receive messages between software components. The intention of this
spec is to leverage RabbitMQ as the messaging system since it is most
commonly used within the OpenStack community. Clustering and RabbitMQ
Mirrored Queues provide active/active and highly scalable message
queuing for OpenStack services.

* RabbitMQ Clustering: If the RabbitMQ broker consists of a single node,
  then a failure of that node will cause downtime, temporary
  unavailability of service, and potentially loss of messages. A cluster
  of RabbitMQ nodes can be used to construct the RabbitMQ broker.
  Clustering RabbitMQ nodes are resilient to the loss of individual nodes
  in terms of overall availability of the service. All data/state
  required for the operation of a RabbitMQ broker is replicated across
  all nodes, for reliability and scaling. An exception to this are message
  queues, which by default reside on the node that created them, though
  they are visible and reachable from all nodes.

* RabbitMQ Mirrored Queues: While exchanges and bindings survive the loss
  of individual nodes, message queues and their messages do not. This is
  because a queue and its contents reside on exactly one node, thus the
  loss of a node will render its queues unavailable. To solve these
  various problems, RabbitMQ has developed active/active high-availability
  for message queues. This works by allowing queues to be mirrored on
  other nodes within a RabbitMQ cluster. The result is that should one
  node of a cluster fail, the queue can automatically switch to one of the
  mirrors and continue to operate, with no unavailability of service. This
  solution still requires a RabbitMQ Cluster, which means that it will not
  cope seamlessly with network partitions within the cluster and, for that
  reason, is not recommended for use across a WAN (though of course,
  clients can still connect from as near and as far as needed).

HAProxy provide load-balancing between clients and OpenStack API Endpoints.
HAProxy is a free, very fast and reliable software solution offering high
availability, load balancing, and proxying for TCP and HTTP-based
applications. HAProxy implements an event-driven, single-process model
which enables support for a high number of simultaneous connections.

Memcached is required by nova-consoleauth, Horizon and Swift Proxy to store
ephemeral data such as tokens. Memcached does not support typical forms of
redundancy such as clustering. However, OpenStack services can support more
than one Memcached instance by configuring multiple hostnames or IP addresses.
The Memcached client implements hashing to balance objects among the
instances. Failure of a Memcached instance only impacts a portion of the objects
and the client automatically removes it from the list of instances.

An Example configuration with two hosts:
'memcached_servers = kolla1:11211,kolla2:11211'

Memcached does not implement authentication and therefore is insecure.
This risk is reduced in default deployments because Memcached is not exposed
outside of localhost. Since deploying Memcahced in a highly-available manner
requires exposing Memcached outside of localhost, precautions should be taken
to reduce this risk.

Keepalived is routing software that provides simple and robust facilities
for load-balancing Linux systems. Keepalived will track the HAProxy process
and failover/back between HAProxy instances with minimal service interruption.
Keepalived implements the Virtual Router Redundancy Protocol (VRRP).
VRRP creates virtual routers, which are an abstract representation of
multiple routers, i.e. master and backup routers, acting as a group.
The default gateway of a participating host is assigned to the
virtual router instead of a physical router. If the physical router that
is routing packets on behalf of the virtual router fails, another physical
router is selected to automatically replace it. The physical router that
is forwarding packets at any given time is called the master router.

Neutron: HAProxy will provide high-availability and scalability to the
neutron-server service by load-balancing traffic across multiple instances
of the service. RabbitMQ clustering and mirrored queues will be used to
provide high-availability and scalability for RPC messaging among Neutron
components. Galera will provide high-availability and scalability to Neutron
persistent data. Multiple Neutron Agents will be deployed across separate
nodes. [Multiple L3/DHCP Agents][] will be assigned per tenant network to
provide network high-availability for tenant networks.

[Multiple L3/DHCP Agents]: https://wiki.openstack.org/wiki/Neutron/L3_High_Availability_VRRP

Glance: Glance can use different back-ends to store OpenStack images. Examples
include Swift, Ceph, Cinder and the default filesystem back-end. Although
it is not required, it is highly recommended to use a backend that is highly
scalable and fault-tolerant.

Just as with the rest of the OpenStack API's, HAProxy and Keepalived can
provide high-availability and scalability to the Glance API and Registry
endpoints.

Swift: Multiple Swift Proxy services can be used to provide high
availability to the Swift object, account and container storage rings.
Standard Swift replication provides high-availability to data stored within
a Swift object storage system. The replication processes compare local data
with each remote copy to ensure they all contain the latest version. Object
replication uses a hash list to quickly compare subsections of each
partition. Container and account replication use a combination of
hashes and shared high water marks.

Cinder: As with other stateless services, HAProxy can provide high
availability and scalability to cinder-api. RabbitMQ clustering and mirrored
queues can provide high-availability and scalability for RPC messaging among
Cinder services. At the time of this writing, the only Cinder backend
supported is LVM. LVM can be made [highly-available][] or a new Cinder
backend, such as [Ceph][], can be added to Kolla which supports high
availability and scalability for tenant-facing block storage services.
Due to limitations described [here][], the Cinder volume manager can
not be reliably deployed in an active/active or active/passive fashion.

[highly-available]: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Cluster_Administration/ap-ha-halvm-CA.html
[Ceph]: http://ceph.com/
[here]: https://bugs.launchpad.net/cinder/+bug/1322190

In general, the Kolla HA environment looks like:

![Image](https://git.openstack.org/cgit/openstack/kolla/plain/specs/ha.svg)

Security impact
---------------

Keystone UUID vs PKI tokens. Tokens are used as a mechanism to
authenticate API requests of users. Keystone supports UUID and
PKI token formats. PKI tokens provide better security, but are more
difficult to deploy in an active/active manner. Therefore,
it is recommended to start with UUID tokens and add PKI tokens
in a future iteration.

Performance Impact
------------------

The proposed high-availability spec should increase the performance of
Kolla-based OpenStack clouds. A slight performance decrease can be expected due
to the additional hop introduced by the load-balancing layer. However, the
additional latency introduced by this layer is insignificant. Since this layer
provides intelligent load-balancing of services, improved performance can be
expected for services under moderate-to-heavy load. Without the intelligence
provided by the load-balancing layer, overloaded services can become degraded
and a decrease in performance can be expected.

Performance tests should be conducted for the following scenarios to validate
and/or improve the HA spec:

1. The HA environment is functioning as expected.
2. One or more API services are in a failed state.
3. One or more Galera instances are in a failed state.
4. One or more RabbitMQ Brokers are in a failed state.
5. Adding services to/from the HA environment.

Implementation
==============

Generally, the implementation should start off simple and add capabilities
through development iterations. The implementation can be organized as follows:

1. Multi-node: In order to implement HA, Kolla must first support being deployed
to multiple hosts.

2. Database: Implement a Galera container image that follows best practices
used by existing Kolla images. Use existing tools to manage the image,
the configuration file(s) and deployment of the Galera service in a highly
available and scalable fashion.

3. RabbitMQ: Implement a RabbitMQ container image that follows best practices
used by existing Kolla images. Use existing tools to manage the image,
the configuration file(s) and deployment of the Galera service in a highly
available and scalable fashion.

4. APIs: Implement HAProxy/Keepalived container images that follow best practices
used by existing Kolla images. Use existing tools to manage the image,
the configuration file(s) and deployment of the Galera service in a highly
available and scalable fashion.

5. Update Existing Images: Update existing container images with the necessary
configuration to support HA. For example, OpenStack services should use the
Virtual IP of the Galera cluster to communicate with the DB instead of an
IP assigned to an individual DB instance.

6. Update Existing Deployment Automation: Update automation scripts, playbooks,
etc to support additional container images, configuration parameters, etc.
introduced by the HA components.

7. Testing: Follow the guidance provided in the performance impact section to
test how the OpenStack environment responds and performances in various failure
scenarios.

Assignee(s)
-----------

Primary assignee:

kolla maintainers

Work Items
----------

1. Deploy existing Kolla across multiple physical hosts.
2. Create containers for HAProxy, Keepalived.
3. Add Galera Support to existing MariaDB container set.
4. Add clustering/mirrored queue support to RabbitMQ container set.
5. Add L3/DHCP agent HA to existing Neutron agent container set.
6. Create Swift containers.
7. Add/configure the Glance backend to support HA and scalability.
8. Add/configure HAproxy for services, like keystone or horizon.

Testing
=======

We don't know how to test multi-node deployment in CI/CD because
we are unsure whether the gating system allows for deployments
consisting of more than one VM. As a result, we will rely on manual
testing of the solution as a starting point.

Documentation Impact
====================

The integration-guide.md should be updated to include additional K/V
pairs introduced by HA. Additionally, a document should be developed
explaining how to deploy and configure Kolla in a highly-available
fashion.

References
==========

* [VRRP] http://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol
