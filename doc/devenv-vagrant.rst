Vagrant up!
===========

This guide describes how to use `Vagrant <http://vagrantup.com>`__ to
assist in developing for Kolla.

Vagrant is a tool to assist in scripted creation of virtual machines. Vagrant
takes care of setting up CentOS-based VMs for Kolla development, each with
proper hardware like memory amount and number of network interfaces.

Getting Started
---------------

The Vagrant script implements All-in-One (AIO) or multi-node deployments. AIO
is the default.

In the case of multi-node deployment, the Vagrant setup builds a cluster with
the following nodes by default:

-  3 control nodes
-  1 compute node
-  1 storage node (Note: ceph requires at least 3 storage nodes)
-  1 network node
-  1 operator node

The cluster node count can be changed by editing the Vagrantfile.

Kolla runs from the operator node to deploy OpenStack.

All nodes are connected with each other on the secondary NIC. The
primary NIC is behind a NAT interface for connecting with the Internet.
The third NIC is connected without IP configuration to a public bridge
interface. This may be used for Neutron/Nova to connect to instances.

Start by downloading and installing the Vagrant package for the distro of
choice. Various downloads can be found at the `Vagrant downloads
<https://www.vagrantup.com/downloads.html>`__.

On Fedora 22 it is as easy as::

    sudo dnf install vagrant ruby-devel libvirt-devel

Next install the hostmanager plugin so all hosts are recorded in /etc/hosts
(inside each vm)::

    vagrant plugin install vagrant-hostmanager

Vagrant supports a wide range of virtualization technologies. This
documentation describes libvirt. The Kolla Vagrantfile uses features not yet
available in a packaged version. To install vagrant-libvirt plugin from git::

    git checkout https://github.com/pradels/vagrant-libvirt.git
    cd vagrant-libvirt
    sudo dnf install rubygem-rake rubygem-bundler
    rake build
    vagrant plugin install pkg/vagrant-libvirt-0.0.30.gem

Setup NFS to permit file sharing between host and VMs. Contrary to rsync
method, NFS allows both way synchronization and offers much better performances
than VirtualBox shared folders. On Fedora 22::

    sudo systemctl start nfs-server
    firewall-cmd --permanent --add-port=2049/udp
    firewall-cmd --permanent --add-port=2049/tcp
    firewall-cmd --permanent --add-port=111/udp
    firewall-cmd --permanent --add-port=111/tcp

Find a location in the system's home directory and checkout the Kolla repo::

    git clone https://github.com/openstack/kolla.git ~/dev/kolla

Developers can now tweak the Vagrantfile or bring up the default AIO
Centos7-based environment::

    cd ~/dev/kolla/vagrant && vagrant up

The command ``vagrant status`` provides a quick overview of the VMs composing
the environment.

Vagrant Up
----------

Once Vagrant has completed deploying all nodes, the next step is to launch
Kolla. First, connect with the *operator* node::

    vagrant ssh operator

To speed things up, there is a local registry running on the operator.  All
nodes are configured so they can use this insecure repo to pull from, and use
it as a mirror. Ansible may use this registry to pull images from.

All nodes have a local folder shared between the group and the hypervisor, and
a folder shared between *all* nodes and the hypervisor.  This mapping is lost
after reboots, so make sure to use the command ``vagrant reload <node>`` when
reboots are required. Having this shared folder provides a method to supply
a different docker binary to the cluster. The shared folder is also used to
store the docker-registry files, so they are save from destructive operations
like ``vagrant destroy``.


Building images
^^^^^^^^^^^^^^^

Once logged on the *operator* VM call the ``kolla-build`` utility::

    kolla-build

``kolla-build`` accept arguments as documented in :doc:`image-building`.


Deploying OpenStack with Kolla
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deploy AIO with::

    sudo kolla-ansible deploy

Deploy multinode with::

    sudo kolla-ansible deploy -i /usr/share/kolla/ansible/inventory/multinode

Validate OpenStack is operational::

    source ~/openrc
    openstack user-list

Or navigate to http://10.10.10.254/ with a web browser.


Further Reading
---------------

All Vagrant documentation can be found at
`docs.vagrantup.com <http://docs.vagrantup.com>`__.
