Vagrant up!
============================

This guide describes how to use [Vagrant][] to assist in developing for Kolla.

Vagrant is a tool to assist in scripted creation of virtual machines, it will
take care of setting up a CentOS-based cluster of virtual machines, each with
proper hardware like memory amount and number of network interfaces.

[Vagrant]: http://vagrantup.com


Getting Started
---------------

The vagrant setup will build a cluster with the following nodes:

- 3 control nodes
- 1 compute node
- 1 operator node

Kolla runs from the operator node to deploy OpenStack on the other nodes.

All nodes are connected with each other on the secondary nic, the primary nic
is behind a NAT interface for connecting with the internet. A third nic is
connected without IP configuration to a public bridge interface. This may be
used for Neutron/Nova to connect to instances.

Start with downloading and installing the Vagrant package for your distro of
choice. Various downloads can be found [here][]. After we will install the
hostmanager plugin so all hosts are recorded in /etc/hosts (inside each vm):

    vagrant plugin install vagrant-hostmanager

Vagrant supports a wide range of virtualization technologies, of which we will
use VirtualBox for now.

Find some place in your homedir and checkout the Kolla repo

    git clone https://github.com/stackforge/kolla.git ~/dev/kolla

You can now tweak the Vagrantfile or start a CentOS7-based cluster right away:

    cd ~/dev/kolla/vagrant && vagrant up

The command `vagrant up` will build your cluster, `vagrant status` will give
you a quick overview once done.

[here]: https://www.vagrantup.com/downloads.html

Vagrant Up
---------

Once vagrant has completed deploying all nodes, we can focus on launching Kolla.
First, connect with the _operator_ node:

    vagrant ssh operator

Once connected you can run a simple Ansible-style ping to verify if the cluster is operable:

    ansible -i kolla/ansible/inventory/multinode all -m ping -e ansible_ssh_user=root

Congratulations, your cluster is usable and you can start deploying OpenStack using Ansible!

To speed things up, there is a local registry running on the operator. All nodes are configured
so they can use this insecure repo to pull from, and they will use it as mirror. Ansible may
use this registry to pull images from.

All nodes have a local folder shared between the group and the hypervisor, and a folder shared
between _all_ nodes and the hypervisor. This mapping is lost after reboots, so make sure you use
the command `vagrant reload <node>` when reboots are required. Having this shared folder you
have a method to supply a different docker binary to the cluster. The shared folder is also
used to store the docker-registry files, so they are save from destructive operations like
`vagrant destroy`.

Further Reading
---------------

All Vagrant documentation can be found on their [website][].

[website]: http://docs.vagrantup.com
