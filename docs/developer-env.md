# Developer env

In order to run Kolla, it is mandatory to run a version of
`docker-compose` that includes pid: host support.  One of the
authors of Kolla has a pull request outstanding that the
docker-compose maintainers have said they would merge shortly.

The pull request is:

    https://github.com/docker/compose/pull/1011

Until then, it must be retrieved via git and installed:

    git pull http://github.com/sdake/fig
    cd fig
    sudo pip install .
    sudo pip install -U docker-py

The docker-compose version available via the sdake repository has been
rebased on to a master version of docker-compose which requires the
docker API 1.18.  the docker API 1.18 is not available in distro
packaging and is only available by building from source.  Docker also
distributes pre-built binaries for docker.  It is recommended to just run
the docker provided binaries rather then building from source:

    sudo systemctl stop docker
    sudo killall -9 docker
    curl https://master.dockerproject.com/linux/amd64/docker-1.5.0-dev -o docker-dev
    sudo ./docker-dev -d

The basic starting environment will be created using `docker-compose`.
This environment will start up the openstack services listed in the
compose directory.

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

# Debug

You can follow a container's status by doing

    $ sudo docker ps -a

If any of the containers exited you can check the logs by doing

    $ sudo docker logs <glance-api-container>
    $ docker-compose logs <glance-api-container>

If you want to start a individual service like `glance-api` by hand, then use
this template.  This is a good method to test and troubleshoot an individual
container.

    $ docker run --name glance-api -d \
             --net=host
             --env-file=openstack.env kollaglue/fedora-rdo-glance-api:latest
