.. quickstart:

===========
Quick Start
===========

This guide provides step by step instructions to deploy OpenStack using Kolla
and Kolla-Ansible on bare metal servers or virtual machines.

Host machine requirements
=========================

The host machine must satisfy the following minimum requirements:

- 2 network interfaces
- 8GB main memory
- 40GB disk space

.. note::

    Root access to the deployment host machine is required.

Recommended environment
=======================

This guide recommends using a bare metal server or a virtual machine. Follow
the instructions in this document to get started with deploying OpenStack on
bare metal or a virtual machine with Kolla.

If developing Kolla on a system that provides VirtualBox or Libvirt in addition
to Vagrant, use the Vagrant virtual environment documented in
:doc:`vagrant-dev-env`.

Prerequisites
=============

Verify the state of network interfaces. If using a VM spawned on
OpenStack as the host machine, the state of the second interface will be DOWN
on booting the VM.

::

    ip addr show

Bring up the second network interface if it is down.

::

    ip link set ens4 up

Verify if the second interface has an IP address.

::

    ip addr show

Install dependencies
====================

Kolla builds images which are used by Kolla-Ansible to deploy OpenStack. The
deployment is tested on CentOS, Oracle Linux and Ubuntu as both container OS
platforms and bare metal deployment targets.

Ubuntu: For Ubuntu based systems where Docker is used it is recommended to use
the latest available LTS kernel. While all kernels should work for Docker, some
older kernels may have issues with some of the different Docker back ends such
as AUFS and OverlayFS. In order to update kernel in Ubuntu 14.04 LTS to 4.2,
run:

::

    apt-get install linux-image-generic-lts-wily

.. note:: Install is *very* sensitive about version of components. Please
   review carefully because default Operating System repos are likely out of
   date.

Dependencies for the stable/mitaka branch are:

=====================   ===========  ===========  =========================
Component               Min Version  Max Version  Comment
=====================   ===========  ===========  =========================
Ansible                 1.9.4        <2.0.0       On deployment host
Docker                  1.10.0       none         On target nodes
Docker Python           1.6.0        none         On target nodes
Python Jinja2           2.6.0        none         On deployment host
=====================   ===========  ===========  =========================

Dependencies for the stable/newton branch and later (including master branch)
are:

=====================   ===========  ===========  =========================
Component               Min Version  Max Version  Comment
=====================   ===========  ===========  =========================
Ansible                 2.0.0        none         On deployment host
Docker                  1.10.0       none         On target nodes
Docker Python           1.6.0        none         On target nodes
Python Jinja2           2.8.0        none         On deployment host
=====================   ===========  ===========  =========================

Make sure the ``pip`` package manager is installed and upgraded to the latest
before proceeding:

::

    #CentOS
    yum install epel-release
    yum install python-pip
    pip install -U pip

    #Ubuntu
    apt-get update
    apt-get install python-pip
    pip install -U pip

Install dependencies needed to build the code with ``pip`` package manager.

::

    #CentOS
    yum install python-devel libffi-devel gcc openssl-devel

    #Ubuntu
    apt-get install python-dev libffi-dev gcc libssl-dev

Kolla deploys OpenStack using `Ansible <http://www.ansible.com>`__. Install
Ansible from distribution packaging if the distro packaging has recommended
version available.

Some implemented distro versions of Ansible are too old to use distro
packaging. Currently, CentOS and RHEL package Ansible >2.0 which is suitable
for use with Kolla. Note that you will need to enable access to the EPEL
repository to install via yum -- to do so, take a look at Fedora's EPEL `docs
<https://fedoraproject.org/wiki/EPEL>`__ and `FAQ
<https://fedoraproject.org/wiki/EPEL/FAQ>`__.

On CentOS or RHEL systems, this can be done using:

::

    yum install ansible

Many DEB based systems do not meet Kolla's Ansible version requirements. It is
recommended to use pip to install Ansible >2.0. Finally Ansible >2.0 may be
installed using:

::

    pip install -U ansible

.. note:: It is recommended to use virtualenv to install non-system packages.

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

The following dependencies can be installed by bootstraping the host machine
as described in the `Automatic host bootstrap`_ section. For manual
installation, follow the instructions below:

Since Docker is required to build images as well as be present on all deployed
targets, the Kolla community recommends installing the official Docker, Inc.
packaged version of Docker for maximum stability and compatibility with the
following command:

::

    curl -sSL https://get.docker.io | bash

This command will install the most recent stable version of Docker, but please
note that Kolla releases are not in sync with Docker in any way, so some things
could stop working with new version. The latest release of Kolla is tested to
work with docker-engine >= 1.10.0. To check your Docker version run this
command:

::

    docker --version

When running with systemd, setup docker-engine with the appropriate information
in the Docker daemon to launch with. This means setting up the following
information in the ``docker.service`` file. If you do not set the MountFlags
option correctly then ``kolla-ansible`` will fail to deploy the
``neutron-dhcp-agent`` container and throws APIError/HTTPError. After adding
the drop-in unit file as follows, reload and restart the Docker service:

::

    # Create the drop-in unit directory for docker.service
    mkdir -p /etc/systemd/system/docker.service.d

    # Create the drop-in unit file
    tee /etc/systemd/system/docker.service.d/kolla.conf <<-'EOF'
    [Service]
    MountFlags=shared
    EOF

Restart Docker by executing the following commands:

::

    # Run these commands to reload the daemon
    systemctl daemon-reload
    systemctl restart docker

On the target hosts you also need an updated version of the Docker python
libraries:

.. note:: The old docker-python is obsoleted by python-docker-py.

::

    yum install python-docker-py


Or using ``pip`` to install the latest version:

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

   /usr/sbin/libvirtd: error while loading shared libraries:
   libvirt-admin.so.0: cannot open shared object file: Permission denied

If you are seeing the libvirt container fail with the error above, disable the
libvirt profile.

::

    sudo apparmor_parser -R /etc/apparmor.d/usr.sbin.libvirtd


.. note::

    On Ubuntu 16.04, please uninstall lxd and lxc packages. (An issue exists
    with cgroup mounts, mounts exponentially increasing when restarting
    container).

Additional steps for upstart and other non-systemd distros
==========================================================

For Ubuntu 14.04 which uses upstart and other non-systemd distros, run the
following.

::

    mount --make-shared /run
    mount --make-shared /var/lib/nova/mnt

If /var/lib/nova/mnt is not present, can do below work around.

::

    mkdir -p /var/lib/nova/mnt /var/lib/nova/mnt1
    mount --bind /var/lib/nova/mnt1 /var/lib/nova/mnt
    mount --make-shared /var/lib/nova/mnt

For mounting /run and /var/lib/nova/mnt as shared upon startup, edit
/etc/rc.local to add the following.

::

    mount --make-shared /run
    mount --make-shared /var/lib/nova/mnt

.. note::

    If CentOS/Fedora/OracleLinux container images are built on an Ubuntu host,
    the back-end storage driver must not be AUFS (see the known issues in
    :doc:`image-building`).

Install Kolla for deployment or evaluation
==========================================

Install Kolla and its dependencies using pip.

::

    pip install kolla

Copy the configuration files globals.yml and passwords.yml to /etc directory.

::

    #CentOS
    cp -r /usr/share/kolla/etc_examples/kolla /etc/kolla/

    #Ubuntu
    cp -r /usr/local/share/kolla/etc_examples/kolla /etc/kolla/

The inventory files (all-in-one and multinode) are located in
/usr/local/share/kolla/ansible/inventory. Copy the configuration files to the
current directory.

::

   #CentOS
   cp /usr/share/kolla/ansible/inventory/* .

   #Ubuntu
   cp /usr/local/share/kolla/ansible/inventory/* .

Install Kolla for development
=============================

Clone the Kolla and Kolla-Ansible repositories from git.

::

    git clone https://github.com/openstack/kolla
    git clone https://github.com/openstack/kolla-ansible

Kolla-ansible holds configuration files (globals.yml and passwords.yml) in
etc/kolla.  Copy the configuration files to /etc directory.

::

    cp -r kolla-ansible/etc/kolla /etc/kolla/

Kolla-ansible holds the inventory files (all-in-one and multinode) in
ansible/inventory. Copy the configuration files to the current directory.

::

    cp kolla-ansible/ansible/inventory/* .

Local Registry
==============

A local registry is recommended but not required for an ``all-in-one``
installation when developing for master. Since no master images are available
on docker hub, the docker cache may be used for all-in-one deployments.  When
deploying multinode, a registry is strongly recommended to serve as a single
source of images. Reference the :doc:`multinode` for more information on using
a local Docker registry. Otherwise, the Docker Hub Image Registry contains all
images from each of Kolla’s major releases. The latest release tag is 3.0.2 for
Newton.

Automatic host bootstrap
========================

Edit the ``/etc/kolla/globals.yml`` file to configure interfaces.

::

    network_interface: "ens3"
    neutron_external_interface: "ens4"

Generate passwords. This will populate all empty fields in the
``/etc/kolla/passwords.yml`` file using randomly generated values to secure the
deployment. Optionally, the passwords may be populated in the file by hand.

::

    kolla-genpwd

To quickly prepare hosts, playbook bootstrap-servers can be used.This is an
Ansible playbook which works on Ubuntu 14.04, 16.04 and CentOS 7 hosts to
install and prepare the cluster for OpenStack installation.

::

    kolla-ansible -i <<inventory file>> bootstrap-servers

Build container images
======================

When running with systemd, edit the file
``/etc/systemd/system/docker.service.d/kolla.conf``
to include the MTU size to be used for Docker containers.

::

    [Service]
    MountFlags=shared
    ExecStart=
    ExecStart=/usr/bin/docker daemon \
     -H fd:// \
     --mtu 1400

.. note::

    The MTU size should be less than or equal to the MTU size allowed on the
    network interfaces of the host machine. If the MTU size allowed on the
    network interfaces of the host machine is 1500 then this step can be
    skipped. This step is relevant for building containers. Actual openstack
    services won't be affected.

.. note::

   Verify that the MountFlags parameter is configured as shared. If you do not
   set the MountFlags option correctly then kolla-ansible will fail to deploy the
   neutron-dhcp-agent container and throws APIError/HTTPError.

Restart Docker and ensure that Docker is running.

::

    systemctl daemon-reload
    systemctl restart docker

The Kolla community builds and pushes tested images for each tagged release of
Kolla.  Pull required images with appropriate tags.

::

    kolla-ansible pull

View the images.

::

    docker images

Developers running from master are required to build container images as
the Docker Hub does not contain built images for the master branch.
Reference the :doc:`image-building` for more advanced build configuration.

To build images using default parameters run:

::

    kolla-build

By default kolla-build will build all containers using CentOS as the base image
and binary installation as base installation method. To change this behavior,
please use the following parameters with kolla-build:

::

    --base [ubuntu|centos|oraclelinux]
    --type [binary|source]

.. note::

    --base and --type can be added to the above kolla-build command if
    different distributions or types are desired.

It is also possible to build individual container images. As an example, if the
glance images failed to build, all glance related images can be rebuilt as
follows:

::

    kolla-build glance

In order to see all available parameters, run:

::

    kolla-build -h

View the images.

::

    docker images

.. WARNING::
    Mixing of OpenStack releases with Kolla releases (example, updating
    kolla-build.conf to build Mitaka Keystone to be deployed with Newton Kolla) is
    not recommended and will likely cause issues.

Deploy Kolla
============

Kolla-Ansible is used to deploy containers by using images built by Kolla.
There are two methods of deployment: *all-in-one* and *multinode*.  The
*all-in-one* deployment is similar to `devstack
<http://docs.openstack.org/developer/devstack/>`__ deploy which installs all
OpenStack services on a single host. In the *multinode* deployment, OpenStack
services can be run on specific hosts. This documentation describes deploying
an *all-in-one* setup. To setup *multinode* see the :doc:`multinode`.

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
parameters: ``kolla_base_distro``, ``kolla_install_type``. The default for
``kolla_base_distro`` is ``centos`` and for ``kolla_install_type`` is
``binary``. If you want to use ubuntu with source type, then you should make
sure globals.yml has the following entries:

::

    kolla_base_distro: "ubuntu"
    kolla_install_type: "source"

Please specify an unused IP address in the network to act as a VIP for
``kolla_internal_vip_address``. The VIP will be used with keepalived and added
to the ``api_interface`` as specified in the ``globals.yml``

::

    kolla_internal_vip_address: “192.168.137.79”

.. note::

    The kolla_internal_vip_address must be unique and should belong to the same
    network to which the first network interface belongs to.

.. note::

    The kolla_base_distro and kolla_install_type should be same as base and
    install_type used in kolla-build command line.

The ``network_interface`` variable is the interface to which Kolla binds API
services. For example, when starting Mariadb, it will bind to the IP on the
interface list in the ``network_interface`` variable.

::

    network_interface: "ens3"

The ``neutron_external_interface`` variable is the interface that will be used
for the external bridge in Neutron. Without this bridge the deployment instance
traffic will be unable to access the rest of the Internet.

::

    neutron_external_interface: "ens4"

In case of deployment using the **nested** environment (eg. Using Virtualbox
VM’s, KVM VM’s), verify if your compute node supports hardware acceleration for
virtual machines by executing the following command in the *compute node*.

::

    egrep -c '(vmx|svm)' /proc/cpuinfo

If this command returns a value of **zero**, your compute node does not support
hardware acceleration and you **must** configure libvirt to use **QEMU**
instead of KVM. Create a file /etc/kolla/config/nova/nova-compute.conf and add
the content shown below.

::

    mkdir /etc/kolla/config/nova
    cat << EOF > /etc/kolla/config/nova/nova-compute.conf
    [libvirt]
    virt_type=qemu
    EOF

For *all-in-one* deployments, the following commands can be run. These will
setup all of the containers on the localhost. These commands will be
wrapped in the kolla-script in the future.

.. note:: Even for all-in-one installs it is possible to use the Docker
   registry for deployment, although not strictly required.

First, validate that the deployment targets are in a state where Kolla may
deploy to them. Provide the correct path to inventory file in the following
commands.

::

    kolla-ansible prechecks -i /path/to/all-in-one

Deploy OpenStack.

::

    kolla-ansible deploy -i /path/to/all-in-one

List the running containers.

::

    docker ps -a

Generate the ``admin-openrc.sh`` file. The file will be created in
``/etc/kolla/`` directory.

::

    kolla-ansible post-deploy

To test your deployment, run the following commands to initialize the network
with a glance image and neutron networks.

::

    source /etc/kolla/admin-openrc.sh

    #centOS
    cd /usr/share/kolla
    ./init-runonce

    #ubuntu
    cd /usr/local/share/kolla
    ./init-runonce

.. note::

    Different hardware results in results in variance with deployment times.

After successful deployment of OpenStack, the Horizon dashboard will be
available by entering IP address or hostname from ``kolla_external_fqdn``, or
``kolla_internal_fqdn``. If these variables were not set during deploy they
default to ``kolla_internal_vip_address``.

.. _Docker Hub Image Registry: https://hub.docker.com/u/kolla/
.. _launchpad bug: https://bugs.launchpad.net/kolla/+filebug
