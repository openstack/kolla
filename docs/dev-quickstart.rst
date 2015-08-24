Quickstart to Deploying OpenStack using Ansible
===============================================

Evaluation and Developer Environments
-------------------------------------

Two virtualized evaluation and development environment options are
available.  These options permit the evaluation of Kolla without
disrupting the host operating system.

If developing or evaluating Kolla on an OpenStack cloud environment that
supports Heat, follow the
`Heat evaluation and developer environment guide <https://github.com/stackforge/kolla/blob/master/docs/devenv-heat.rst>`__.

If developing or evaluating Kolla on a system that provides VirtualBox,
Vagrant may be used and is documented in the
`Vagrant evaluation and developer environment guide <https://github.com/stackforge/kolla/blob/master/docs/devenv-vagrant.rst>`__.

If evaluating or deploying OpenStack on bare-metal with Kolla, follow the
instructions in this document to get started.

Installing Dependencies
-----------------------

Kolla is tested on Fedora/Ubuntu/CentOS. It should work with other OS
distributions, but some need further testing. If other OS distributions can
be verified, update this doc accordingly. For Fedora/Ubuntu, follow below
recommendations:

Fedora: Kolla will not run on Fedora 22 or later currently. Fedora 22
compresses kernel modules with the .xz compressed format. The guestfs system
in the CentOS family of containers cannot read these images because a dependent
package supermin in CentOS needs to be updated to add .xz compressed format
support.

Ubuntu: For Ubuntu based systems where Docker is used, do not use AUFS when
starting Docker daemon unless you are running the Ubuntu with 3.19 kernel or
above. AUFS requires CONFIG\_AUFS\_XATTR=y set when building the kernel. On
Ubuntu, versions prior to 3.19 did not set this flag to be compatible with
Docker. If unable to upgrade the kernel, the Kolla community recommends using
a different storage backend such as btrfs when running Docker dameon.

On the deployment host Ansible>=1.8.4 must be installed and is the only
requirement for deploying OpenStack.  To build the Docker container images
locally the dependnencies docker>=1.7.0 and the Python libraries
docker-py>=1.2.0 and Jinja2>=2.6 must be installed.

The deployment targt nodes require the installation of docker>=1.7.0 and
docker-py>=1.2.0.

To install Kolla Python depenedencies use:

::

    git clone http://github.com/stackforge/kolla
    cd kolla
    sudo pip install -r requirements.txt

Since Docker is required to build images as well as be present on all deployed
targets, the Kolla community recommends installing the Docker Inc. packaged
version of Docker for maximum stability and compatiblity with the following
command:

::

    curl -sSL https://get.docker.io | bash

On the system where the OpenStack CLI/Python code is run, the Kolla community
recommends installing the OpenStack python clients if they are not installed.
This could be a completely different machine then the deployment host or
deployment targets. Before installing the OpenStack python client, there are
the following requirements needed by your system:

::

   # Ubuntu
   sudo apt-get install -y python-dev python-pip libffi-dev libssl-dev

   # Fedora
   sudo yum install -y python-devel python-pip libffi-devel  openssl-devel

   # Centos
   sudo easy_install pip
   sudo yum instal -y python-devel libffi-devel  openssl-devel

To install these clients use:

::

    sudo pip install -U python-openstackclient

Libvirt is started by default on many operating systems.  Please disable libvirt
on any machines that will be deployment targets.  Only one copy of libvirt may
be running at a time.

::

    service libvirtd disable
    service libvirtd stop

Kolla deploys OpenStack using
`Ansible <https://ansible.com>`__.  Install Ansible from distribution
packaging if the distro packaging has 1.8.4 or greater available.  Currently
Ubuntu's version of Ansible is too old to use from packaging.  On RPM
based systems install from packaging using:

::

    yum -y install ansible

On DEB based systems this can be done using:

::

    apt-get install ansible

If the distro packaged version of Ansible is too old, install Ansible using
pip:

::

    pip install -U ansible

Buildling Container Images
--------------------------

The Kolla community does not currently generate new images for each commit
to the repository.  The push time for a full image build to the docker registry
is about 5 hours on 100mbit Internet, so there are technical limitations to
using the Docker Hub registry with our current OpenStack CI/CD systems.

The Kolla community builds and pushes tested images for each tagged release of
Kolla, but if running from master, it is recommended to build images locally.
All Docker images can be built as follows.

Before running the below intructions, make sure docker dameon is running,
or the build process would fail:

::

    tools/build.py -T 1000

The -T option specifies how many threads to run concurrently. A docker build
of all containers on Xeon hardware with SSDs and 100mbit network takes roughly
15 minutes.  The CentOS mirrors are flakey and the RDO delorean repository is
not mirrored at all.  As a result occasionally some containers will fail to
build.  If something important fails to bulid, repeat the entire build process
again.  The Kolla community recognizes this is not ideal and the Kolla community
is adding an individual container build option to solve this particular problem.

Starting Kolla
--------------

Configure Ansible by reading the
`Kolla Ansible configuration Guide <https://github.com/stackforge/kolla/blob/master/docs/ansible-deployment.rst>`__ documentation.

Finally, run the deploy operation:

::

    $ sudo ./tools/kolla-ansible deploy

A bare metal system takes three minutes to deploy AIO. A virtual machine
deployment takes five minutes to deploy AIO. These are estimates; different
hardware may be faster or slower but should be near these results.

Debugging Kolla
---------------

The container's status can be determined on the deployment targets by
executing:

::

    $ docker ps -a

If any of the containers exited, this indicates a bug in the container.  Please
seek help by filing a bug or contacting the developers via IRC.

 the logs can be examined by executing:

::

    $ docker logs <container-name>

Note some of the containers don't log to stdout at present so the above
command will provide no information.  Instead they log to files
in _/var_/log_/_<service_> inside the container.  The Kolla community is
working to improve auditing and make things more consistent.  The Kolla
community expects this work to complete by Liberty rc1.  An example of
reading the logs for nova-api:

::
    $ docker exec -t nova_api more /var/log/nova/nova-api.log

Note reading the logs via an exec operation can only be done if the
container is running.
