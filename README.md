Kolla
=====

The Kolla project is part of the OpenStack TripleO effort, focused on
deploying OpenStack environments using [Kubernetes][] and [Docker][]
containers.

[kubernetes]: https://github.com/GoogleCloudPlatform/kubernetes
[docker]: http://docker.com/

Getting Started
===============

Kubernetes deployment on bare metal is a complex topic which is beyond the
scope of this project at this time.  The developers require a development test
environment.  As a result, one of the developers has created a Heat based
deployment tool that can be
found [here](https://github.com/larsks/heat-kubernetes).


Build Docker Images
-------------------

Images are built by the Kolla project maintainers.  It is possible to build
unique images with specific changes, but these would end up in a personal
namespace.  Read the docs directory image workflow documentation for more
details.

The Kolla developers build images in the kollaglue namespace for the following
services:
* Glance
* Heat
* Keystone
* Mariadb
* Nova
* Rabbitmq

```
$ sudo docker search kollaglue
```
A list of the upstream built docker images will be shown.

Use Kubernetes to Deploy OpenStack
----------------------------------

At this point, we believe the key features for a minimum viable feature set
are implemented.  This includes the capability to launch virtual machines in
Nova.  One key fact is that networking may not entirely work properly yet
until Neutron is finished, so the virtual machines may not actually behave
as expected for an end user deployment.

Two options exist for those without an existing Kubernetes environment:

The upstream Kubernetes community provides instructions for running Kubernetes
using Vagrant, available from:
https://github.com/GoogleCloudPlatform/kubernetes/blob/master/docs/getting-started-guides/vagrant.md

The Kolla developers develop Kolla in OpenStack, using Heat to provision the
necessary servers and other resources.  If you are familiar with Heat and
have a correctly configured environment available, this allows deployment
of a working Kubernetes cluster automatically.  The Heat templates are
available from https://github.com/larsks/heat-kubernetes/.  The templates
require at least Heat 2014.1.3 (earlier versions have a bug that will prevent
the templates from working).

Here are some simple steps to get things rolling using the Heat templates:

1. Clone the repository:
   ```
   git clone https://github.com/larsks/heat-kubernetes/
   cd heat-kubernetes
   ```

2. Create an appropriate image by running the get_image.sh script in this
   repository.  This will generate an image called `fedora-20-k8s.qcow2`.
   Upload this image to Glance.  You can also obtain an appropriate image from
   https://fedorapeople.org/groups/heat/kolla/fedora-20-k8s.qcow2

3. Create a file `local.yaml` with settings appropriate to your OpenStack
   environment. It should look something like:
   ```
   parameters:
     server_image: fedora-20-k8s
     ssh_key_name: sdake


     dns_nameserver: 8.8.8.8
     external_network_id: 6e7e7701-46a0-49c0-9f06-ac5abc79d6ae
     number_of_minions: 1
     server_flavor: m1.large
   ```
   You *must* provide settings for external_network_id and ssh_key_name; these
   are local to your environment. You will probably also need to provide
   a value for server_image, which should be the name (or UUID) of a Fedora 20
   cloud image or derivative.

4. `heat stack-create -f kubecluster.yaml -e local.yaml my-kube-cluster`

5. Determine the ip addresses of your cluster hosts by running:
   ```
   heat output-show my-kube-cluster kube_minions_external
   ```

6. Connect to the minion node with `ssh fedora@${minion-ip}`

7. On the minion node:
   ```
   minion$ git clone http://github.com/stackforge/kolla
   minion$ cd kolla
   minion$ ./tools/start
   ```

Debugging
==========
A few commands for debugging the system.

```
$ sudo docker images
```
Lists all images that have been pulled from the upstream kollaglue repository
thus far.  This can be run on the minion during the `./start` operation to
check on the download progress.


```
$ sudo docker ps -a
```
This will show all processes that docker has started.  Removing the `-a` will
show only active processes.  This can be run on the minion during the `./start`
operation to check that the containers are orchestrated.


```
$ sudo docker logs <containerid>
```
This shows the logging output of each service in a container.  The containerid
can be obtained via the `docker ps` operation.  This can be run on the minion
during the `./start` operation to debug the container.

```
$ kubecfg list pods
```
This lists all pods of which Kubernetes is aware.  This can be run on the
master or minion.

```
$ sudo systemctl restart kube-apiserver
$ sudo systemctl restart kube-scheduler
```
This command is needed on the master after heat finishes the creation of the
Kubernetes system (ie: my-kube-cluster is in CREATE_COMPLETE state).  This is
just a workaround for a bug in kubernetes that should be fixed soon.


```
$ journalctl -f -l -xn -u kube-apiserver -u etcd -u kube-scheduler
```
This shows log output on the server for the various daemons and can be filed
in bug reports in the upstream launchpad tracker.

```
$ journalctl -f -l -xn -u kubelet.service -u kube-proxy -u docker
```
This shows log output on the minion for the various daemons and can be filed
in bug reports in the upstream launchpad tracker.

```
$ telnet minion_ip 3306
```
This shows that the Mariadb service is running on the minions.  Output should
appear as follows

```
$ telnet 10.0.0.4 3306
Trying 10.0.0.4...
Connected to 10.0.0.4.
Escape character is '^]'.

5.5.39-MariaDB-wsrep
```

If the connection closes before mysql responds then the proxy is not properly
connecting to the database.  This can be seen by using jounalctl and watching
for a connection error on the node that you can't connect to mysql through.

```
$ journalctl -f -l -xn -u kube-proxy
```
If you can conect though one and not the other there's probably a problem with
the overlay network. Double check that you're tunning kernel 3.16+ because
vxlan support is required. If you kernel version is good try restarting
openvswitch on both nodes. This has usually fixed the connection issues.

Directories
===========

* docker - contains artifacts for use with docker build to build appropriate
  images
* k8s - contains service and pod configuration information for Kubernetes
* tools - contains different tools for interacting with Kolla
