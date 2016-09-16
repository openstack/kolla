.. quickstart:

===========
Quick Start
===========

This guide provides a step by step of how to deploy Kolla on bare metal or a
virtual machine.

Host machine requirements
=========================

The recommended deployment target requirements:

- 2 (or more) network interfaces.
- At least 8gb main memory
- At least 40gb disk space.

.. note:: Some commands below may require root permissions (e.g. pip, apt-get).

Recommended Environment
=======================

If developing or evaluating Kolla, the community strongly recommends using bare
metal or a virtual machine. Follow the instructions in this document to get
started with deploying OpenStack on bare metal or a virtual machine with Kolla.
There are other deployment environments referenced below in
`Additional Environments`_.

Automatic host bootstrap
========================

.. note:: New in Newton

To quickly prepare hosts for Kolla, playbook ``bootstrap-servers`` can be used.
This is an Ansible playbook which works on Ubuntu 14.04, 16.04 and CentOS 7
hosts to install and prepare cluster for Kolla installation.

.. note:: Installation of dependencies for deployment node and configuration
   of Kolla interfaces is still required prior to running this command. More
   information about Kolla interface configuration in
   :ref:`interface-configuration`.

Command to run the playbook:

::

    kolla-ansible -i <<inventory file>> bootstrap-servers

To learn more about the inventory file, follow :ref:`edit-inventory`.


Install Dependencies
====================

Kolla is tested on CentOS, Oracle Linux, RHEL and Ubuntu as both container OS
platforms and bare metal deployment targets.

Fedora: Kolla will not run on Fedora 22 and later as a bare metal deployment
target. These distributions compress kernel modules with the .xz compressed
format. The guestfs system in the CentOS family of containers cannot read
these images because a dependent package supermin in CentOS needs to be updated
to add .xz compressed format support.

Ubuntu: For Ubuntu based systems where Docker is used it is recommended to use
the latest available LTS kernel. The latest LTS kernel available is the wily
kernel (version 4.2). While all kernels should work for Docker, some older
kernels may have issues with some of the different Docker backends such as AUFS
and OverlayFS. In order to update kernel in Ubuntu 14.04 LTS to 4.2, run:

::

    apt-get install linux-image-generic-lts-wily

.. WARNING::
   Operators performing an evaluation or deployment should use a stable
   branch. Operators performing development (or developers) should use
   master.

.. note:: Install is *very* sensitive about version of components. Please
  review carefully because default Operating System repos are likely out of
  date.

Dependencies for the stable branch are:

=====================   ===========  ===========  =========================
Component               Min Version  Max Version  Comment
=====================   ===========  ===========  =========================
Ansible                 1.9.4        < 2.0.0      On deployment host
Docker                  1.10.0       none         On target nodes
Docker Python           1.6.0        none         On target nodes
Python Jinja2           2.6.0        none         On deployment host
=====================   ===========  ===========  =========================


Dependencies for the master branch are:

=====================   ===========  ===========  =========================
Component               Min Version  Max Version  Comment
=====================   ===========  ===========  =========================
Ansible                 2.0.0        none         On deployment host
Docker                  1.10.0       none         On target nodes
Docker Python           1.6.0        none         On target nodes
Python Jinja2           2.8.0        none         On deployment host
=====================   ===========  ===========  =========================

Make sure the ``pip`` package manager is installed and upgraded to latest
before proceeding:

::

    # CentOS 7
    yum install epel-release
    yum install python-pip

    # Ubuntu 14.04 LTS
    apt-get install python-pip

    # Upgrade pip and check version
    pip install -U pip
    pip -V


Since Docker is required to build images as well as be present on all deployed
targets, the Kolla community recommends installing the official Docker, Inc.
packaged version of Docker for maximum stability and compatibility with the
following command:

::

    curl -sSL https://get.docker.io | bash

This command will install the most recent stable version of Docker, but please
note that Kolla releases are not in sync with docker in any way, so some things
could stop working with new version. The latest release of Kolla is tested to
work with docker-engine >= 1.10.0. To check your docker version run this
command:

::

    docker --version

When running with systemd, setup docker-engine with the appropriate information
in the Docker daemon to launch with. This means setting up the following
information in the ``docker.service`` file. If you do not set the MountFlags
option correctly then ``kolla-ansible`` will fail to deploy the
``neutron-dhcp-agent`` container and throws APIError/HTTPError. After adding
the drop-in unit file as follows, reload and restart the docker service:

::

    # Create the drop-in unit directory for docker.service
    mkdir -p /etc/systemd/system/docker.service.d

    # Create the drop-in unit file
    tee /etc/systemd/system/docker.service.d/kolla.conf <<-'EOF'
    [Service]
    MountFlags=shared
    EOF

Restart docker by executing the following commands:

::

    # Run these commands to reload the daemon
    systemctl daemon-reload
    systemctl restart docker

For Ubuntu 14.04 which uses upstart and other non-systemd distros,
run the following:

::

    mount --make-shared /run

For mounting ``/run`` as shared upon startup, add that command to
``/etc/rc.local``

::

    # Edit /etc/rc.local to add:
    mount --make-shared /run

.. note:: If centos/fedora/oraclelinux container images are built on an Ubuntu
  host, the backend storage driver must not be AUFS (see the known issues in
  :doc:`image-building`).

.. note:: On ubuntu 16.04, please uninstall ``lxd`` and ``lxc`` packages. (issue
  with cgroup mounts, mounts exponentially increasing when restarting container).

On the target hosts you also need an updated version of the Docker python
libraries:

.. note:: The old docker-python is obsoleted by python-docker-py.

::

    yum install python-docker-py


Or using ``pip`` to install a latest version:

::

    pip install -U docker-py


OpenStack, RabbitMQ, and Ceph require all hosts to have matching times to
ensure proper message delivery. In the case of Ceph, it will complain if the
hosts differ by more than 0.05 seconds. Some OpenStack services have timers as
low as 2 seconds by default. For these reasons it is highly recommended to
setup an NTP service of some kind. While ``ntpd`` will achieve more accurate
time for the deployment if the NTP servers are running in the local deployment
environment, `chrony <http://chrony.tuxfamily.org>`_ is more accurate when
syncing the time across a WAN connection. When running Ceph it is recommended
to setup ``ntpd`` to sync time locally due to the tight time constraints.

To install, start, and enable ntp on CentOS execute the following:

::

    # CentOS 7
    yum install ntp
    systemctl enable ntpd.service
    systemctl start ntpd.service

To install and start on Debian based systems execute the following:

::

    apt-get install ntp

Libvirt is started by default on many operating systems. Please disable
``libvirt`` on any machines that will be deployment targets. Only one copy of
libvirt may be running at a time.

::

    # CentOS 7
    systemctl stop libvirtd.service
    systemctl disable libvirtd.service

    # Ubuntu
    service libvirt-bin stop
    update-rc.d libvirt-bin disable

On Ubuntu, apparmor will sometimes prevent libvirt from working.

::

   /usr/sbin/libvirtd: error while loading shared libraries: libvirt-admin.so.0: cannot open shared object file: Permission denied

If you are seeing the libvirt container fail with the error above, disable the
libvirt profile.

::

   sudo apparmor_parser -R /etc/apparmor.d/usr.sbin.libvirtd


Kolla deploys OpenStack using `Ansible <http://www.ansible.com>`__. Install
Ansible from distribution packaging if the distro packaging has recommended
version available.

Some implemented distro versions of Ansible are too old to use distro
packaging. Currently, CentOS and RHEL package Ansible >2.0 which is suitable
for use with Kolla. Note that you will need to enable access to the EPEL
repository to install via yum -- to do so, take a look at Fedora's EPEL
`docs <https://fedoraproject.org/wiki/EPEL>`__ and
`FAQ <https://fedoraproject.org/wiki/EPEL/FAQ>`__.

On CentOS or RHEL systems, this can be done using:

::

    yum install ansible

Many DEB based systems do not meet Kolla's Ansible version requirements. It is
recommended to use pip to install Ansible >2.0. Finally Ansible >2.0 may be
installed using:

::

    pip install -U ansible

If DEB based systems include a version of Ansible that meets Kolla's version
requirements it can be installed by:

::

    apt-get install ansible

.. WARNING::
   Kolla uses PBR in its implementation. PBR provides version information
   to Kolla about the package in use. This information is later used when
   building images to specify the Docker tag used in the image built. When
   installing the Kolla package via pip, PBR will always use the PBR version
   information. When obtaining a copy of the software via git, PBR will use
   the git version information, but **ONLY** if Kolla has not been pip
   installed via the pip package manager. This is why there is an operator
   workflow and a developer workflow.

Installing Kolla for evaluation or deployment
---------------------------------------------

Install Kolla and its dependencies:

::

    pip install kolla

Copy the Kolla configuration files to ``/etc``:

::
    
    # CentOS 7
    cp -r /usr/share/kolla/etc_examples/kolla /etc/

    # Ubuntu
    cp -r /usr/local/share/kolla/etc_examples/kolla /etc/

Installing Kolla and dependencies for development
-------------------------------------------------

To clone the Kolla repo:

::

    git clone https://git.openstack.org/openstack/kolla

To install Kolla's Python dependencies use:

::

    pip install -r kolla/requirements.txt -r kolla/test-requirements.txt

.. note:: This does not actually install Kolla. Many commands in this documentation are named
    differently in the tools directory.

Kolla holds configurations files in ``etc/kolla``. Copy the configuration files
to ``/etc``:

::

    cd kolla
    cp -r etc/kolla /etc/

Install Python Clients
======================

On the system where the OpenStack CLI/Python code is run, the Kolla community
recommends installing the OpenStack python clients if they are not installed.
This could be a completely different machine then the deployment host or
deployment targets. The following requirements are needed to build the
client code:

::

   # Ubuntu
   apt-get install python-dev libffi-dev libssl-dev gcc

   # CentOS 7
   yum install python-devel libffi-devel openssl-devel gcc


To install the clients use:

::

    yum install python-openstackclient python-neutronclient


Or using ``pip`` to install:

::

    pip install -U python-openstackclient python-neutronclient

Local Registry
==============

A local registry is not required for an ``all-in-one`` installation. Check out
the :doc:`multinode` for more information on using a local registry. Otherwise,
the `Docker Hub Image Registry`_ contains all images from each of Kolla's major
releases. The latest release tag is 2.0.0 for Mitaka.

Additional Environments
=======================

Two virtualized development environment options are available for Kolla. These
options permit the development of Kolla without disrupting the host operating
system.

If developing Kolla on a system that provides VirtualBox or Libvirt in addition
to Vagrant, use the Vagrant virtual environment documented in
:doc:`vagrant-dev-env`.

Building Container Images
=========================

The Kolla community builds and pushes tested images for each tagged release of
Kolla, but if running from master, it is recommended to build images locally.

Checkout the :doc:`image-building` for more advanced build configuration.

Before running the below instructions, ensure the docker daemon is running
or the build process will fail. To build images using default parameters run:

::

    kolla-build

By default ``kolla-build`` will build all containers using CentOS as the base
image and binary installation as base installation method. To change this
behavior, please use the following parameters with ``kolla-build``:

::

--base [ubuntu|centos|fedora|oraclelinux]
--type [binary|source]

If pushing to a local registry (recommended) use the flags:

::

    kolla-build --registry registry_ip_address:registry_ip_port --push

Note ``--base`` and ``--type`` can be added to the above ``kolla-build``
command if different distributions or types are desired.

It is also possible to build individual containers. As an example, if the
glance containers failed to build, all glance related containers can be rebuilt
as follows:

::

    kolla-build glance

In order to see all available parameters, run:

::

    kolla-build -h

For more information about building Kolla container images, check the detailed
instruction in :doc:`image-building`.

.. _deploying-kolla:

Deploying Kolla
===============

The Kolla community provides two example methods of Kolla deploy: *all-in-one*
and *multinode*. The *all-in-one* deploy is similar to
`devstack <http://docs.openstack.org/developer/devstack/>`__ deploy which
installs all OpenStack services on a single host. In the *multinode* deploy,
OpenStack services can be run on specific hosts. This documentation only
describes deploying *all-in-one* method as most simple one. To setup
*multinode* see the :doc:`multinode`.

Each method is represented as an Ansible inventory file. More information on
the Ansible inventory file can be found in the Ansible `inventory introduction
<https://docs.ansible.com/intro_inventory.html>`__.

All variables for the environment can be specified in the files:
``/etc/kolla/globals.yml`` and ``/etc/kolla/passwords.yml``.

Generate passwords for ``/etc/kolla/passwords.yml`` using the provided
``kolla-genpwd`` tool. The tool will populate all empty fields in the
``/etc/kolla/passwords.yml`` file using randomly generated values to secure the
deployment. Optionally, the passwords may be populate in the file by hand.

::

    kolla-genpwd

Start by editing ``/etc/kolla/globals.yml``. Check and edit, if needed, these
parameters: ``kolla_base_distro``, ``kolla_install_type``. These parameters
should match what you used in the ``kolla-build`` command line. The default for
``kolla_base_distro`` is ``centos`` and for ``kolla_install_type`` is
``binary``. If you want to use ubuntu with source type, then you should make
sure ``globals.yml`` has the following entries:

::

  kolla_base_distro: "ubuntu"
  kolla_install_type: "source"


Please specify an unused IP address in the network to act as a VIP for
``kolla_internal_vip_address``. The VIP will be used with keepalived and added
to the ``api_interface`` as specified in the ``globals.yml`` ::

    kolla_internal_vip_address: "10.10.10.254"

The ``network_interface`` variable is the interface to which Kolla binds API
services. For example, when starting up Mariadb it will bind to the IP on the
interface list in the ``network_interface`` variable. ::

    network_interface: "eth0"

The ``neutron_external_interface`` variable is the interface that will be used
for the external bridge in Neutron. Without this bridge the deployment instance
traffic will be unable to access the rest of the Internet. In the case of a
single interface on a machine, a veth pair may be used where one end of the
veth pair is listed here and the other end is in a bridge on the system. ::

    neutron_external_interface: "eth1"

If using a local docker registry, set the ``docker_registry`` information where
the local registry is operating on IP address 192.168.1.100 and the port 4000.

::

    docker_registry: "192.168.1.100:4000"

For *all-in-one* deploys, the following commands can be run. These will
setup all of the containers on the localhost. These commands will be
wrapped in the kolla-script in the future.

.. note:: Even for all-in-one installs it is possible to use the docker
   registry for deployment, although not strictly required.

First, check that the deployment targets are in a state where Kolla may deploy
to them:

::

    kolla-ansible prechecks

Verify that all required images with appropriate tags are available:

::

    kolla-ansible pull

Run the deployment:

::

    kolla-ansible deploy

If APIError/HTTPError is received from the neutron-dhcp-agent container,
remove the container and recreate it:

::

    docker rm -v -f neutron_dhcp_agent
    kolla-ansible deploy

In order to see all available parameters, run:

::

    kolla-ansible -h

.. note:: In case of deploying using the _nested_ environment (*eg*.
  Using Virtualbox VM's, KVM VM's), if your compute node supports
  hardware acceleration for virtual machines.

  For this, run the follow command in **compute node**:

::

    $ egrep -c '(vmx|svm)' /proc/cpuinfo


If this command returns a value of **zero**, your compute node does not
support hardware acceleration and you **must** configure libvirt to use
**QEMU** instead of KVM.

For this, change the **virt_type** option in the `[libvirt]` section
of **nova-compute.conf** file inside the ``/etc/kolla/config/`` directory.

::

    [libvirt]
    virt_type=qemu

A bare metal system with Ceph takes 18 minutes to deploy. A virtual machine
deployment takes 25 minutes. These are estimates; different hardware may be
faster or slower but should be near these results.

After successful deployment of OpenStack, the Horizon dashboard will be
available by entering IP address or hostname from ``kolla_external_fqdn``, or
``kolla_internal_fqdn``. If these variables were not set during deploy they
default to ``kolla_internal_vip_address``.

Useful tools
------------
After successful deployment of OpenStack, run the following command can create
an openrc file ``/etc/kolla/admin-openrc.sh`` on the deploy node. Or view
``tools/openrc-example`` for an example of an openrc that may be used with the
environment.

::

    kolla-ansible post-deploy

After the openrc file is created, use the following command to initialize an
environment with a glance image and neutron networks:

::

    . /etc/kolla/admin-openrc.sh
    kolla/tools/init-runonce

Failures
========

Nearly always when Kolla fails, it is caused by a CTRL-C during the deployment
process or a problem in the ``globals.yml`` configuration.

To correct the problem where Operators have a misconfigured environment, the
Kolla developers have added a precheck feature which ensures the deployment
targets are in a state where Kolla may deploy to them. To run the prechecks,
execute:

::

    kolla-ansible prechecks

If a failure during deployment occurs it nearly always occurs during evaluation
of the software. Once the Operator learns the few configuration options
required, it is highly unlikely they will experience a failure in deployment.

Deployment may be run as many times as desired, but if a failure in a
bootstrap task occurs, a further deploy action will not correct the problem.
In this scenario, Kolla's behavior is undefined.

The fastest way during evaluation to recover from a deployment failure is to
remove the failed deployment:

On each node where OpenStack is deployed run:

::

    tools/cleanup-containers
    tools/cleanup-host

The Operator will have to copy via scp or some other means the cleanup scripts
to the various nodes where the failed containers are located.

Any time the tags of a release change, it is possible that the container
implementation from older versions won't match the Ansible playbooks in a new
version. If running multinode from a registry, each node's Docker image cache
must be refreshed with the latest images before a new deployment can occur. To
refresh the docker cache from the local Docker registry:

::

    kolla-ansible pull

Debugging Kolla
===============

The container's status can be determined on the deployment targets by
executing:

::

    docker ps -a

If any of the containers exited, this indicates a bug in the container. Please
seek help by filing a `launchpad bug`_ or contacting the developers via IRC.

The logs can be examined by executing:

::

    docker exec -it heka bash

The logs from all services in all containers may be read from
``/var/log/kolla/SERVICE_NAME``

If the stdout logs are needed, please run:

::

    docker logs <container-name>

Note that most of the containers don't log to stdout so the above command will
provide no information.

To learn more about Docker command line operation please refer to `Docker
documentation <https://docs.docker.com/reference/commandline/cli/>`__.

When ``enable_central_logging`` is enabled, to view the logs in a web browser
using Kibana, go to:

::

    http://<kolla_internal_vip_address>:<kibana_server_port>
    or http://<kolla_external_vip_address>:<kibana_server_port>

and authenticate using ``<kibana_user>`` and ``<kibana_password>``.

The values ``<kolla_internal_vip_address>``, ``<kolla_external_vip_address>``
``<kibana_server_port>`` and ``<kibana_user>`` can be found in
``<kolla_install_path>/kolla/ansible/group_vars/all.yml`` or if the default
values are overridden, in ``/etc/kolla/globals.yml``. The value of
``<kibana_password>`` can be found in ``/etc/kolla/passwords.yml``.

.. note:: When you log in to Kibana web interface for the first time, you are
          prompted to create an index. Please create an index using the name ``log-*``.
          This step is necessary until the default Kibana dashboard is implemented in
          Kolla.

.. _Docker Hub Image Registry: https://hub.docker.com/u/kolla/
.. _launchpad bug: https://bugs.launchpad.net/kolla/+filebug
