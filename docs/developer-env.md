# Developer Environment

If you are developing Kolla on an existing OpenStack cloud
that supports Heat, then follow the Heat template [README][].
Otherwise, follow the instructions below to manually create
your Kolla development environment.

[README]: https://github.com/stackforge/kolla/tree/version-m3/devenv/README.md

## Installing Dependencies

In order to run Kolla, it is mandatory to run a version of
`docker-compose` that includes pid: host support.  The `docker-compose`
master repo includes support but the pip packaged version of 1.2.0 does not.
we expect the pip packaged version of docker-compose 1.3.0 to include
the necessary features, so these next steps won't be necessary if installed
from pip or distro packaging.

    git clone http://github.com/docker/compose
    cd compose
    sudo pip install -e .

In order to run Kolla, it is mandatory to run a version of `docker`
that is a 1.6.0 release candidate greater then rc3.  Docker calls increasing
the rc version number an "RC Bump".  To read the RC Bump thread where images
can be downloaded:

    https://github.com/docker/docker/pull/11635#issuecomment-90293460

If a version of Docker less than 1.6.0-rc3 is running on your system, stop it:

    sudo systemctl stop docker
    sudo killall -9 docker

Next, download and run the Docker 1.6.0-rc5 provided by jessfraz (Docker Inc.
Employee):

    curl https://test.docker.com/builds/Linux/x86_64/docker-1.6.0-rc5 -o docker
    sudo ./docker -d &

Finally stop libvirt on the host machine.  Only one copy of libvirt may be
running at a time.

    service libvirtd stop

The basic starting environment will be created using `docker-compose`.
This environment will start up the openstack services listed in the
compose directory.

## Starting Kolla

To start, setup your environment variables.

    $ cd kolla
    $ ./tools/genenv

The `genenv` script will create a compose/openstack.env file
and an openrc file in your current directory. The openstack.env
file contains all of your initialized environment variables, which
you can edit for a different setup.

Next, run the start script.

    $ ./tools/start

The `start` script is responsible for starting the containers
using `docker-compose -f <osp-service-container> up -d`.

If you want to start a container set by hand use this template

    $ docker-compose -f glance-api-registry.yml up -d

## Debugging Kolla

All Docker commands should be run from the directory of the Docker binary,
by default this is `/`.

You can follow a container's status by doing

    $ sudo ./docker ps -a

If any of the containers exited you can check the logs by doing

    $ sudo ./docker logs <container-id>
    $ docker-compose logs <container-id>

If you want to start a individual service like `glance-api` by hand, then use
this template.  This is a good method to test and troubleshoot an individual
container.  Note some containers require special options.  Reference the
compose yml specification for more details:

    $ sudo ./docker run --name glance-api -d \
             --net=host
             --env-file=openstack.env kollaglue/fedora-rdo-glance-api:latest
