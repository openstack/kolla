A Kolla Cluster with Heat
=========================

These [Heat][] templates will deploy an *N*-node [Kolla][] cluster,
where *N* is the value of the `number_of_nodes` parameter you
specify when creating the stack.

Kolla has recently undergone a considerable design change. The details
of the design change is addressed in this [spec][]. As part of the
design change, containers share pid and networking namespaces with
the Docker host. Therefore, containers no longer connect to a docker0
bridge and have separate networking from the host. As a result, Kolla
networking has a configuration similar to:

![Image](https://raw.githubusercontent.com/stackforge/kolla/master/devenv/kollanet.png)

Sharing pid and networking namespaces is detailed in the 
[super privileged containers][] concept.

The Kolla cluster is based on Fedora 21, and makes use of the
[pkilambi/docker][] [COPR][] repository for Docker packages. This
is because Kolla requires a newer version of Docker not currently
packaged in Fedora 21.

These templates are designed to work with the Icehouse or Juno
versions of Heat. If using Icehouse Heat, this [patch][] is
required to correct a bug with template validation when using the
"Fn::Join" function).

[heat]: https://wiki.openstack.org/wiki/Heat
[kolla]: https://launchpad.net/kolla
[pkilambi/docker]: https://copr.fedoraproject.org/coprs/pkilambi/docker
[copr]: https://copr.fedoraproject.org/
[spec]: https://review.openstack.org/#/c/153798/
[super privileged containers]: http://sdake.io/2015/01/28/an-atomic-upgrade-process-for-openstack-compute-nodes/
[patch]: https://review.openstack.org/#/c/121139/

Create the Glance Image
=======================

After cloning the project, run the get-image.sh script from the project's
devenv directory:

    $ ./get-image.sh

The script will create a Fedora 21 image with the required modifications.

Copy the image to your Glance image store:

    $ glance image-create --name "fedora-21-x86_64" \
    --file /var/lib/libvirt/images/fedora-21-x86_64 \
    --disk-format qcow2 --container-format bare \
    --is-public True --progress

Create the Stack
================

Copy local.yaml.example to local.yaml and edit the contents to match
your deployment environment. Here is an example of a customized
local.yaml:

    parameters:
      ssh_key_name: admin-key
      external_network_id: 028d70dd-67b8-4901-8bdd-0c62b06cce2d
      dns_nameserver: 192.168.200.1

Review the parameters section of kollacluster.yaml for a full list of
configuration options. **Note:** You must provide values for:

- `ssh_key_name`
- `external_network_id`

And then create the stack, referencing that environment file:

    $ heat stack-create -f kollacluster.yaml -e local.yaml kolla-cluster

Access the Kolla Nodes
======================

You can get the ip address of the Kolla nodes using the `heat
output-show` command:

    $ heat output-show kolla-cluster kolla_node_external_ip
    "192.168.200.86"

You can ssh into that server as the `fedora` user:

    $ ssh fedora@192.168.200.86

And once logged in you can run Docker commands, etc:

    $ sudo docker images

Debugging
==========
A few commands for debugging the system.

```
$ sudo docker images
```
Lists all images that have been pulled from the upstream kollaglue repository
thus far.  This can be run on the node during the `./start` operation to
check on the download progress.

```
$ sudo docker ps -a
```
This will show all processes that docker has started.  Removing the `-a` will
show only active processes.  This can be run on the node during the `./start`
operation to check that the containers are orchestrated.

```
$ sudo docker logs <containerid>
```
This shows the logging output of each service in a container.  The containerid
can be obtained via the `docker ps` operation.  This can be run on the node
during the `./start` operation to debug the container.

```
$ sudo systemctl restart docker
```
Restarts the Docker service on the node.

```
$ journalctl -f -l -xn -u docker
```
This shows log output on the server for the docker daemon and can be filed
in bug reports in the upstream launchpad tracker.

```
$ telnet <NODE_IP> 3306
```
You can use telnet to test connectivity to a container. This example demonstrates
the Mariadb service is running on the node.  Output should appear as follows

```
$ telnet 10.0.0.4 3306
Trying 10.0.0.4...
Connected to 10.0.0.4.
Escape character is '^]'.

5.5.39-MariaDB-wsrep
```
