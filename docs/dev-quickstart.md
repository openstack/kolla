# Developer Environment

If you are developing Kolla on an existing OpenStack cloud
that supports Heat, then follow the Heat template [README][].
Otherwise, follow the instructions below to manually create
your Kolla development environment.

[README]: https://github.com/stackforge/kolla/blob/master/devenv/README.md

## Installing Dependencies

NB: Kolla will not run on Fedora 22 or later.  Fedora 22 compresses kernel
modules with the .xz compressed format.  The guestfs system cannot read
these images because a dependent package supermin in CentOS needs to be
updated to add .xz compressed format support.

In order to run Kolla, it is mandatory to run a version of `docker-compose`
that includes pid: host support.  The `docker-compose` master repository
includes support but the pip packaged version of 1.2.0 does not.  We expect
the pip packaged version of docker-compose 1.3.0 to include the necessary
features, so these next steps won't be necessary if installed from pip or
distro packaging.

    git clone http://github.com/docker/compose
    cd compose
    sudo pip install -e .

In order to run Kolla, it is mandatory to run a version of `docker`
that is 1.7.0-dev or later.  Docker 1.5.0 has a defect in `--pid=host`
support where the libvirt container cannot be stopped.  Docker 1.6.0 lacks
specific features needed by the master of Kolla.  Docker 1.7.0-dev introduces
mount propogation which is necessary for Neutron thin containers
and bindmounting of the /dev filesystem which is mandatory for the cinder
container.

If a version of Docker less than 1.7.0-dev is running on your system, stop it:

    sudo systemctl stop docker
    sudo killall -9 docker

If using an RPM based system, use the Docker 1.7.0-dev RPMs provided by the
Fedora project:

    sudo rpm -Uvh --nodeps https://kojipkgs.fedoraproject.org//packages/docker/1.7.0/6.git56481a3.fc23/x86_64/docker-1.7.0-6.git56481a3.fc23.x86_64.rpm

For Debian based systems, use the Docker installation tool provided by Docker,
Inc.:

    curl -sSL https://test.docker.com/ | sh

For Ubuntu based systems, use the Docker installation tool provided by Docker,
Inc.:

    curl -sSL https://test.docker.com/ubuntu | sh

Next, install the OpenStack python clients if they are not installed:

    sudo yum install python-keystoneclient python-glanceclient \
      python-novaclient python-heatclient python-neutronclient

Finally stop libvirt on the host machine.  Only one copy of libvirt may be
running at a time.

    service libvirtd stop

The basic starting environment will be created using `docker-compose`.
This environment will start up the OpenStack services listed in the
compose directory.

## Starting Kolla

To start, setup your environment variables.

    $ cd kolla
    $ ./tools/genenv

The `genenv` script will create a compose/openstack.env file
and an openrc file in your current directory. The openstack.env
file contains all of your initialized environment variables, which
you can edit for a different setup.

A mandatory step is customizing the FLAT_INTERFACE network interface
environment variable.  The variable defaults to eth1.  In some cases, the
second interface in a system may not be eth1, but a unique name.  For
example with an Intel driver, the interface is enp1s0.  The interface name
can be determined by executing the ifconfig tool.  The second interface must
be a real interface, not a virtual interface.  Make certain to store the
interface name in `compose/openstack.env`:

    NEUTRON_FLAT_NETWORK_INTERFACE=enp1s0
    FLAT_INTERFACE=enp1s0

Next, run the start command:

    $ sudo ./tools/kolla start

Finally, run the status command:

    $ sudo ./tools/kolla status

This will display information about all Kolla containers.

## Debugging Kolla

All Docker commands should be run from the directory of the Docker binary,
by default this is `/`.

The `start` command to Kolla is responsible for starting the containers
using `docker-compose -f <service-container> up -d`.

If you want to start a container set by hand use this template:

    $ docker-compose -f glance-api-registry.yml up -d


You can determine a container's status by executing:

    $ sudo ./docker ps -a

If any of the containers exited you can check the logs by executing:

    $ sudo ./docker logs <container-id>
    $ docker-compose logs <container-id>

If you want to start a individual service like `glance-api` manually, use
this template.  This is a good method to test and troubleshoot an individual
container.  Note some containers require special options.  Reference the
compose yml specification for more details:

    $ sudo ./docker run --name glance-api -d \
             --net=host \
             --env-file=compose/openstack.env \
             kollaglue/fedora-rdo-glance-api:latest
