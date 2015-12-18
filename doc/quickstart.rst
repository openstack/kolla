Bare Metal Deployment of Kolla
==============================

Evaluation and Developer Environments
-------------------------------------

Two virtualized evaluation and development environment options are
available. These options permit the evaluation of Kolla without
disrupting the host operating system.

If developing or evaluating Kolla on an OpenStack cloud environment that
supports Heat, follow the :doc:`Heat evaluation and developer environment
guide <heat-dev-env>`.

If developing or evaluating Kolla on a system that provides VirtualBox or
Libvirt in addition to Vagrant, use the Vagrant virtual environment documented
in :doc:`Vagrant evaluation and
developer environment guide <vagrant-dev-env>`.

If evaluating or deploying OpenStack on bare-metal with Kolla, follow the
instructions in this document to get started.

Host machine requirements
-------------------------

The recommended deployment target requirements:

- Two network interfaces.
- More than 8gb main memory.
- At least 40gb disk space.

Installing Dependencies
-----------------------

Kolla is tested on CentOS, Oracle Linux, RHEL and Ubuntu as both container
OS platforms and bare metal deployment targets.

Fedora: Kolla will not run on Fedora 22 and later as a bare metal deployment
target. These distributions compress kernel modules with the .xz compressed
format. The guestfs system in the CentOS family of containers cannot read
these images because a dependent package supermin in CentOS needs to be
updated to add .xz compressed format support.

Ubuntu: For Ubuntu based systems where Docker is used, do not use AUFS when
starting Docker daemon, unless running Ubuntu uses 3.19 kernel or above.
AUFS requires CONFIG\_AUFS\_XATTR=y set when building the kernel. On
Ubuntu, versions prior to 3.19 did not set this flag to be compatible with
Docker. In order to update kernel in Ubuntu 14.04 LTS to 3.19, run:

::

    sudo apt-get install linux-image-generic-lts-vivid

If unable to upgrade the kernel, the Kolla community recommends using a
different storage backend such as btrfs when running Docker daemon.

.. NOTE:: Install is *very* sensitive about version of components.  Please
  review carefully because default Operating System repos are likely out of
  date.

=====================   ===========  ===========  =========================
Component               Min Version  Max Version  Comment
=====================   ===========  ===========  =========================
Ansible                 1.9.4        none         On deployment host
Docker                  1.8.2        1.8.2        On target nodes
Docker Python           1.2.0        none         On target nodes
Python Jinja2           2.6.0        none         On deployment host
=====================   ===========  ===========  =========================

Make sure "pip" package manager is installed before procceed:

::

    # Centos 7
    easy_install pip

    # Ubuntu 14.04 LTS
    sudo apt-get install python-pip

To install Kolla tools and Python dependencies use:

::

    git clone https://git.openstack.org/openstack/kolla
    pip install kolla/

Copy Kolla configuration to /etc:

::

    cp -r kolla/etc/kolla /etc/

Kolla release 1.0.0-liberty has been tested to work with docker 1.8.2, to check 
your docker version run this command:

::

    docker --version

Docker 1.8.3 and later are incompatible with Kolla.  If the version installed
is 1.8.3 or later, consider downgrading by using these commands:

::

    # Centos 7
    yum downgrade docker-engine-1.8.2
    systemctl restart docker.service

    # Ubuntu 14.04 LTS
    sudo apt-get install docker-engine=1.8.2-0~trusty

On the system where the OpenStack CLI/Python code is run, the Kolla community
recommends installing the OpenStack python clients if they are not installed.
This could be a completely different machine then the deployment host or
deployment targets. Before installing the OpenStack python client, the
following requirements are needed to build the client code:

::

   # Ubuntu
   sudo apt-get install -y python-dev libffi-dev libssl-dev gcc

   # Centos 7
   yum install -y python-devel libffi-devel openssl-devel gcc

To install these clients use:

::

    pip install -U python-openstackclient

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

Currently all implemented distro versions of Ansible are too old to use distro
packaging.  Once distro packaging is updated install from packaging using:

::

    yum -y install ansible

On DEB based systems this can be done using:

::

    apt-get install ansible

If the distro packaged version of Ansible is too old, install Ansible using
pip:

::

    pip install -U ansible

Some ansible dependencies, like pycrypto, may need gcc installed on the build
system. Install it using system packaging tools if it's not installed already:

::

    # Centos 7
    yum -y install gcc

    # Ubuntu
    sudo apt-get install gcc

Deploy a registry (required for multinode)
------------------------------------------

A Docker registry is a locally hosted registry that replaces the need
to pull from the Docker Hub to get images. Kolla can function with
or without a local registry, however for a multinode deployment a registry
is required.

Currently, the Docker registry v2 has extremely bad performance
because all container data is pushed for every image rather than taking
advantage of Docker layering to optimize push operations.  For more
information reference
`pokey registry <https://github.com/docker/docker/issues/14018>`__.

There are two ways to set up a local docker registry.  Either use packages
or pull the registry container from the Docker Hub.  The packaged Docker
registry is v1 and the container is v2.  For CentOS, the Docker registry v1
is a good alternative while Docker works to solve the v2 github issue
mentioned above.  Unfortunately, not all distributions package
docker-registry.  Note that the v1 registry can be run from Docker containers
by using the registry:latest tag.  However, the current latest tag is broken
and crashes on startup.  Therefore, on Centos use the follow operations
to start the docker-registry v1:

::

    # CentOS

    yum install docker-registry
    sed -i "s/REGISTRY_PORT=5000/REGISTRY_PORT=4000/g" /etc/sysconfig/registry
    systemctl daemon-reload
    systemctl enable docker-registry
    systemctl start docker-registry

If not using CentOS or Docker registry version 2 is desired, run the following
command:

::

    docker run -d -p 4000:5000 --restart=always --name registry registry:2

Note: Kolla looks for the Docker registry to use port 4000. (Docker default is port 5000)

After enabling the registry, it is necessary to instruct docker that it will
be communicating with an insecure registry.  To enable insecure registry
communication on CentOS, modify the "/etc/sysconfig/docker" file to contain
the following where 192.168.1.100 is the IP address of the machine where the
registry is currently running:

::

    other_args="--insecure-registry 192.168.1.100:4000

Docker Inc's packaged version of docker-engine for CentOS is defective and
does not read the other_args configuration options from
"/etc/sysconfig/docker".  To rectify this problem, set the contents of
"/usr/lib/systemd/system/docker.service" to:

::

    [Unit]
    Description=Docker Application Container Engine
    Documentation=https://docs.docker.com
    After=network.target docker.socket
    Requires=docker.socket

    [Service]
    EnvironmentFile=/etc/sysconfig/docker
    Type=notify
    ExecStart=/usr/bin/docker daemon -H fd:// $other_args
    MountFlags=slave
    LimitNOFILE=1048576
    LimitNPROC=1048576
    LimitCORE=infinity

    [Install]
    WantedBy=multi-user.target

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

Start by editing /etc/kolla/globals.yml. Check and edit, if needed, these
parameters: kolla_base_distro, kolla_install_type.

The kolla\_\*\_address variables can both be the same. Please specify
an unused IP address in the network to act as a VIP for
kolla\_internal\_address. The VIP will be used with keepalived and
added to the "api\_interface" as specified in the globals.yml

::

    kolla_external_address: "openstack.example.com"
    kolla_internal_address: "10.10.10.254"

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

The docker\_pull\_policy specifies whether Docker should always pull
images from the repository it is configured for, or only in the case
where the image isn't present locally. If building local images without
pushing them to the Docker registry or a local registry, please set this
value to "missing" or when running deployment Docker will attempt to
fetch the latest image upstream.

::

    docker_pull_policy: "missing"

If using a local docker registry, set the docker\_registry information where
the local registry is operating on IP address 192.168.1.100 and the port 4000.

::

    docker_registry: "192.168.1.100:4000"

For "all-in-one" deploys, the following commands can be run. These will
setup all of the containers on the localhost. These commands will be
wrapped in the kolla-script in the future.  Note even for all-in-one installs
it is possible to use the docker registry for deployment, although not
strictly required.

::

    kolla-ansible deploy

In order to see all available parameters, run:

::

    kolla-ansible -h

A bare metal system with Ceph takes 18 minutes to deploy. A virtual machine
deployment takes 25 minutes. These are estimates; different hardware may be
faster or slower but should be near these results.

After successful deployment of OpenStack, the Horizon dashboard will be
available by entering IP addr or hostname from "kolla_external_address",
or kolla_internal_address in case then kolla_external_address uses
kolla_internal_address.

Useful tools
-------------
If run with the post-deploy.yml, an openrc file is created as
\/etc\/kolla\/admin-openrc.sh on the deploy node. Or view tools/openrc-example
for an example of an openrc that may be used with the environment. The
following command will initialize an environment with a glance image and
neutron networks:

::

    source /etc/kolla/admin-openrc.sh
    kolla/tools/init-runonce

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

    docker exec -it rsyslog bash

The logs from all services in all containers may be read from
/var/log/SERVICE_NAME

If the stdout logs are needed, please run:

::

    docker logs <container-name>

Note that some of the containers don't log to stdout at present so the above
command will provide no information.

To learn more about Docker command line operation please refer to `Docker
documentation <https://docs.docker.com/reference/commandline/cli/>`__.
