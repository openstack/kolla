Deployment of Kolla on Bare Metal or Virtual Machine
====================================================

Evaluation and Developer Environments
-------------------------------------

Two virtualized development environment options are available for Kolla.
These options permit the development of Kolla without disrupting the host
operating system.

If developing Kolla on an OpenStack cloud environment that supports Heat,
follow the :doc:`Heat developer environment guide <heat-dev-env>`.

If developing Kolla on a system that provides VirtualBox or Libvirt in addition
to Vagrant, use the Vagrant virtual environment documented in
:doc:`Vagrant developer environment guide <vagrant-dev-env>`.

If evaluating Kolla, the community strongly recommends using bare metal or a
virtual machine during the evaluation period. Follow the instructions in this
document to get started with deploying OpenStack on bare metal or a virtual
machine with Kolla.

Host machine requirements
-------------------------

The recommended deployment target requirements:

- 2 (or more) network interfaces.
- At least 8gb main memory
- At least 40gb disk space.

.. NOTE:: Some commands below may require root permissions (e.g. pip, apt-get).

Installing Dependencies
-----------------------

Kolla is tested on CentOS, Oracle Linux, RHEL and Ubuntu as both container
OS platforms and bare metal deployment targets.

Fedora: Kolla will not run on Fedora 22 and later as a bare metal deployment
target. These distributions compress kernel modules with the .xz compressed
format. The guestfs system in the CentOS family of containers cannot read
these images because a dependent package supermin in CentOS needs to be
updated to add .xz compressed format support.

Ubuntu: For Ubuntu based systems where Docker is used it is recommended to use
the latest available LTS kernel. The latest LTS kernel available is the wily
kernel (version 4.2). While all kernels should work for Docker, some older
kernels may have issues with some of the different Docker backends such as AUFS
and OverlayFS. In order to update kernel in Ubuntu 14.04 LTS to 4.2, run:

::

    apt-get install linux-image-generic-lts-wily

.. NOTE:: Install is *very* sensitive about version of components.  Please
  review carefully because default Operating System repos are likely out of
  date.

=====================   ===========  ===========  =========================
Component               Min Version  Max Version  Comment
=====================   ===========  ===========  =========================
Ansible                 1.9.4        < 2.0.0      On deployment host
Docker                  1.10.0       none         On target nodes
Docker Python           1.6.0        none         On target nodes
Python Jinja2           2.6.0        none         On deployment host
=====================   ===========  ===========  =========================

Make sure the "pip" package manager is installed before proceeding:

::

    # Centos 7
    easy_install pip

    # Ubuntu 14.04 LTS
    apt-get install python-pip

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

When running with systemd, setup docker-engine with the appropriate
information in the Docker daemon to launch with. This means setting up the
following information in the docker.service file. If you do not set the
MountFlags option correctly then Kolla-Ansible will fail to deploy the
neutron-dhcp-agent container and throws APIError/HTTPError. After adding the
drop-in unit file as follows, reload and restart the docker service:

::

    # Create the drop-in unit directory for docker.service
    mkdir -p /etc/systemd/system/docker.service.d

    # Create the drop-in unit file
    tee /etc/systemd/system/docker.service.d/kolla.conf <<-'EOF'
    [Service]
    MountFlags=shared
    EOF

    # Run these commands to reload the daemon
    systemctl daemon-reload
    systemctl restart docker

For Ubuntu 14.04 which uses upstart instead of systemd, run the following:

::

    mount --make-shared /run

On the system where the OpenStack CLI/Python code is run, the Kolla community
recommends installing the OpenStack python clients if they are not installed.
This could be a completely different machine then the deployment host or
deployment targets. Before installing the OpenStack python client, the
following requirements are needed to build the client code:

::

   # Ubuntu
   apt-get install -y python-dev libffi-dev libssl-dev gcc git

   # Centos 7
   yum install -y python-devel libffi-devel openssl-devel gcc git

To install these clients use:

::

    pip install -U python-openstackclient

To clone the Kolla repo:

::

    git clone https://git.openstack.org/openstack/kolla

To install Kolla tools and Python dependencies use:

::

    pip install kolla/

Copy Kolla configuration to /etc:

::

    cd kolla
    cp -r etc/kolla /etc/

Optionally, you can install tox and generate the build configuration using
following steps.

::

    pip install tox
    tox -e genconfig

The location of the generated configuration file is ``etc/kolla/kolla-build.conf``,
You can also copy it to ``/etc/kolla``. The default location is one of
``/etc/kolla/kolla-build.conf`` or ``etc/kolla/kolla-build.conf``.

OpenStack, RabbitMQ, and Ceph require all hosts to have matching times to ensure
proper message delivery. In the case of Ceph, it will complain if the hosts
differ by more than 0.05 seconds. Some OpenStack services have timers as low as
2 seconds by default. For these reasons it is highly recommended to setup an NTP
service of some kind. While `ntpd` will achieve more accurate time for the
deployment if the NTP servers are running in the local deployment environment,
`chrony <http://chrony.tuxfamily.org>`_ is more accurate when syncing the time
across a WAN connection. When running Ceph it is recommended to setup `ntpd` to
sync time locally due to the tight time constraints.

To install, start, and enable ntp on CentOS execute the following:

::

    # Centos 7
    yum -y install ntp
    systemctl enable ntpd.service
    systemctl start ntpd.service

To install and start on Debian based systems execute the following:

::

    apt-get install ntp

Libvirt is started by default on many operating systems. Please disable libvirt
on any machines that will be deployment targets. Only one copy of libvirt may
be running at a time.

::

    # Centos 7
    systemctl stop libvirtd.service
    systemctl disable libvirtd.service

    # Ubuntu
    service libvirt-bin stop
    update-rc.d libvirt-bin disable

Kolla deploys OpenStack using
`Ansible <http://www.ansible.com>`__. Install Ansible from distribution
packaging if the distro packaging has recommended version available.

Some implemented distro versions of Ansible are too old to use distro
packaging.  Currently, CentOS and RHEL package Ansible 1.9.4 which is
suitable for use with Kolla. Note that you will need to enable access
to the EPEL repository to install via yum -- to do so, take a look at
Fedora's EPEL `docs <https://fedoraproject.org/wiki/EPEL>`__ and
`FAQ <https://fedoraproject.org/wiki/EPEL/FAQ>`__.

On CentOS or RHEL systems, this can be done using:

::

    yum -y install ansible

Many DEB based systems do not meet Kolla's Ansible version requirements.
It is recommended to use pip to install Ansible 1.9.4.

Some ansible dependencies, like pycrypto, may need gcc installed on the build
system. Install it using system packaging tools if it's not installed already:

::

    # Centos 7
    yum -y install gcc

    # Ubuntu
    apt-get install gcc

Finally Ansible 1.9.4 may be installed using:

::

    pip install -U ansible==1.9.4

If DEB based systems include a version of Ansible that meets Kolla's
version requirements it can be installed by:

::

    apt-get install ansible


Deploy a registry (required for multinode)
------------------------------------------

A Docker registry is a locally hosted registry that replaces the need
to pull from the Docker Hub to get images. Kolla can function with
or without a local registry, however for a multinode deployment a registry
is required.

The Docker registry prior to version 2.3 has extremely bad performance
because all container data is pushed for every image rather than taking
advantage of Docker layering to optimize push operations.  For more
information reference
`pokey registry <https://github.com/docker/docker/issues/14018>`__.

The Kolla community recommends using registry 2.3 or later. To deploy
registry 2.3 do the following:

::

    docker run -d -p 4000:5000 --restart=always --name registry registry:2

Note: Kolla looks for the Docker registry to use port 4000. (Docker default
is port 5000)

After enabling the registry, it is necessary to instruct Docker that it will
be communicating with an insecure registry.  To enable insecure registry
communication on CentOS, modify the "/etc/sysconfig/docker" file to contain
the following where 192.168.1.100 is the IP address of the machine where the
registry is currently running:

::

    other_args="--insecure-registry 192.168.1.100:4000"

Docker Inc's packaged version of docker-engine for CentOS is defective and
does not read the other_args configuration options from
"/etc/sysconfig/docker".  To rectify this problem, ensure the
following lines appear in the drop-in unit file at
"/etc/systemd/system/docker.service.d/kolla.conf":

::

    [Service]
    EnvironmentFile=/etc/sysconfig/docker
    # It's necessary to clear ExecStart before attempting to override it
    # or systemd will complain that it is defined more than once.
    ExecStart=
    ExecStart=/usr/bin/docker daemon -H fd:// $other_args

And restart docker by executing the following commands:

::

    # Centos
    systemctl daemon-reload
    systemctl stop docker
    systemctl start docker

Building Container Images
-------------------------

The Kolla community does not currently generate new images for each commit
to the repository. The push time for a full image build to the docker registry
is about 5 hours on 100mbit Internet, so there are technical limitations to
using the Docker Hub registry with the current OpenStack CI/CD systems.

The Kolla community builds and pushes tested images for each tagged release of
Kolla, but if running from master, it is recommended to build images locally.

Before running the below instructions, ensure the docker daemon is running
or the build process will fail. To build images using default parameters run:

::

    kolla-build

By default kolla-build will build all containers using Centos as the base
image and binary installation as base installation method. To change this
behavior, please use the following parameters with kolla-build:

::

--base [ubuntu|centos|fedora|oraclelinux]
--type [binary|source]

If pushing to a local registry (recommended) use the flags:

::

    kolla-build --registry registry_ip_address:registry_ip_port --push

Note --base and --type can be added to the above kolla-build command if
different distributions or types are desired.

A docker build of all containers on Xeon hardware with NVME SSDs and
100mbit network takes roughly 30 minutes to a v1 Docker registry.  The CentOS
mirrors are flakey and the RDO delorean repository is not mirrored at all.  As
a result occasionally some containers fail to build. To rectify build
problems, the build tool will automatically attempt three retries of a build
operation if the first one fails.

It is also possible to build individual containers. As an example, if the
glance containers failed to build, all glance related containers can be
rebuilt as follows:

::

    kolla-build glance

In order to see all available parameters, run:

::

    kolla-build -h

Deploying Kolla
---------------

The Kolla community provides two example methods of Kolla
deploy: *all-in-one* and *multinode*. The "all-in-one" deploy is similar
to `devstack <http://docs.openstack.org/developer/devstack/>`__ deploy which
installs all OpenStack services on a single host. In the "multinode" deploy,
OpenStack services can be run on specific hosts. This documentation only
describes deploying *all-in-one* method as most simple one.

Each method is represented as an Ansible inventory file. More information on
the Ansible inventory file can be found in the Ansible `inventory introduction
<https://docs.ansible.com/intro_inventory.html>`__.

All variables for the environment can be specified in the files:
"/etc/kolla/globals.yml" and "/etc/kolla/passwords.yml"

Generate passwords for /etc/kolla/passwords.yml using the provided
kolla-genpwd tool.  The tool will populate all empty fields in the
"/etc/kolla/passwords.yml" file using randomly generated values to secure the
deployment.  Optionally, the passwords may be populate in the file by hand.

::

    kolla-genpwd

Start by editing /etc/kolla/globals.yml. Check and edit, if needed, these
parameters: kolla_base_distro, kolla_install_type.

Please specify an unused IP address in the network to act as a VIP for
kolla\_internal\_vip\_address. The VIP will be used with keepalived and
added to the "api\_interface" as specified in the globals.yml

::

    kolla_internal_vip_address: "10.10.10.254"

If the environment doesn't have a free IP address available for VIP
configuration, the host's IP address may be used here by disabling HAProxy by
adding:

::

    enable_haproxy: "no"

Note this method is not recommended and generally not tested by the
Kolla community, but included since sometimes a free IP is not available
in a testing environment.

The "network\_interface" variable is the interface to which Kolla binds API
services. For example, when starting up Mariadb it will bind to the
IP on the interface list in the "network\_interface" variable.

::

    network_interface: "eth0"

The "neutron\_external\_interface" variable is the interface that will
be used for the external bridge in Neutron. Without this bridge the deployment
instance traffic will be unable to access the rest of the Internet. In
the case of a single interface on a machine, a veth pair may be used where
one end of the veth pair is listed here and the other end is in a bridge on
the system.

::

    neutron_external_interface: "eth1"

If using a local docker registry, set the docker\_registry information where
the local registry is operating on IP address 192.168.1.100 and the port 4000.

::

    docker_registry: "192.168.1.100:4000"

For "all-in-one" deploys, the following commands can be run. These will
setup all of the containers on the localhost. These commands will be
wrapped in the kolla-script in the future.  Note even for all-in-one installs
it is possible to use the docker registry for deployment, although not
strictly required.

First, check that the deployment targets are in a state where Kolla may deploy
to them:

::

    kolla-ansible prechecks

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

A bare metal system with Ceph takes 18 minutes to deploy. A virtual machine
deployment takes 25 minutes. These are estimates; different hardware may be
faster or slower but should be near these results.

After successful deployment of OpenStack, the Horizon dashboard will be
available by entering IP address or hostname from kolla\_external\_fqdn, or
kolla\_internal\_fqdn. If these variables were not set during deploy they
default to kolla\_internal\_vip\_address.

Useful tools
-------------
After successful deployment of OpenStack, run the following command can create
an openrc file \/etc\/kolla\/admin-openrc.sh on the deploy node. Or view
tools/openrc-example for an example of an openrc that may be used with the
environment.

::

    kolla-ansible post-deploy

After the openrc file is created, use the following command to initialize an
environment with a glance image and neutron networks:

::

    source /etc/kolla/admin-openrc.sh
    kolla/tools/init-runonce

Failures
--------

Nearly always when Kolla fails, it is caused by a CTRL-C during the
deployment process or a problem in the globals.yml configuration.

To correct the problem where Operators have a misconfigured
environment, the Kolla developers have added a precheck feature which
ensures the deployment targets are in a state where Kolla may deploy
to them.  To run the prechecks, execute:

::

    kolla-ansible prechecks

If a failure during deployment occurs it nearly always occurs during
evaluation of the software.  Once the Operator learns the few
configuration options required, it is highly unlikely they will experience
a failure in deployment.

Deployment may be run as many times as desired, but if a failure in a
bootstrap task occurs, a further deploy action will not correct the problem.
In this scenario, Kolla's behavior is undefined.

The fastest way during evaluation to recover from a deployment failure is to
remove the failed deployment:

On each node where OpenStack is deployed run:

::

    tools/cleanup-containers
    tools/cleanup-host

The Operator will have to copy via scp or some other means the cleanup
scripts to the various nodes where the failed containers are located.

Any time the tags of a release change, it is possible that the container
implementation from older versions won't match the Ansible playbooks in
a new version.  If running multinode from a registry, each node's Docker
image cache must be refreshed with the latest images before a new deployment
can occur.  To refresh the docker cache from the local Docker registry:

::

    kolla-ansible pull

Debugging Kolla
---------------

The container's status can be determined on the deployment targets by
executing:

::

    docker ps -a

If any of the containers exited, this indicates a bug in the container. Please
seek help by filing a bug or contacting the developers via IRC.

The logs can be examined by executing:

::

    docker exec -it heka bash

The logs from all services in all containers may be read from
/var/log/kolla/SERVICE_NAME

If the stdout logs are needed, please run:

::

    docker logs <container-name>

Note that most of the containers don't log to stdout so the above command will
provide no information.

To learn more about Docker command line operation please refer to `Docker
documentation <https://docs.docker.com/reference/commandline/cli/>`__.
