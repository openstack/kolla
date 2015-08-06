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
that includes pid: host support. Support was added in version 1.3.0 and is
specified in the requirements.txt. To install this and other potential future
dependencies:

    git clone http://github.com/stackforge/kolla
    cd kolla
    sudo pip install -r requirements.txt

In order to run Kolla, it is mandatory to run a version of `docker` that is
1.6.0 or later.  Docker 1.5.0 has a defect in `--pid=host` support where the
libvirt container cannot be stopped and crashes nova-compute on start.

For most systems you can install the latest stable version of Docker with the
following command:
    curl -sSL https://get.docker.io | bash

For Ubuntu based systems, do not use AUFS when starting Docker daemon unless
you are running the Utopic (3.19) kernel. AUFS requires CONFIG_AUFS_XATTR=y
set when building the kernel. On Ubuntu, versions prior to 3.19 did not set that
flag. If you are unable to upgrade your kernel, you should use a different
storage backend such as btrfs.

Next, install the OpenStack python clients if they are not installed:

    sudo pip install -U python-openstackclient

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

    $ sudo ./tools/kolla-compose start

Finally, run the status command:

    $ sudo ./tools/kolla-compose status

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
