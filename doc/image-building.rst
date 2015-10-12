Image building
==============

The ``tools/build.py`` script in this repository is
responsible for building docker images.

Guide
-----

In general, you will build images like this:

::

    $ tools/build.py

By default, the above command would build all images based on centos image.

If you want to change the base distro image, add ``-b``:

::

    $ tools/build.py -b ubuntu

There are following distros available for building images:

- fedora
- centos
- oraclelinux
- ubuntu

To push the image after building, add ``--push``:

::

    $ tools/build.py --push


If you want to build only keystone image, use the following command:

::

    $ tools/build.py keystone


If you want to build multiple images e.g. keystone and nova, use the following command:

::

    $ tools/build.py keystone nova


``tools/build.py`` use ``kollaglue`` as default namespace. If you
want to push images to your dockerhub, change the namespace like:

::

   $ tools/build.py -n yourusername --push

To push images to local registry, change the namespace, too. If the ip
of the machine running local registry is ``172.22.2.81`` and the port
which local registry listens to is ``4000``, use the following command
to push images to local registry.

::

    tools/build.py --namespace 172.22.2.81:4000/kollaglue --push

To trigger buid.py to pull images from local registry,
the Docker configuration needs to be modified. See
`Docker Insecure Registry Config`_.

The build script reads its configuration from ``/etc/kolla/kolla-build.conf``
or ``etc/kolla/kolla-build.conf``. This is where to change the default
settings.


Build OpenStack from Source
---------------------------

When building images, there are two methods of the OpenStack install.
One is ``binary``. Another is ``source``.
The ``binary`` means that OpenStack will be installed from apt/yum.
And the ``source`` means that OpenStack will be installed from source code.
The default method of the OpenStack install is ``binary``.
You can change it to ``source`` using the following command:

::

    tools/build.py -t source

The locations of OpenStack source code are written in
``etc/kolla/kolla-build.conf``.
Now the source type support ``url`` and ``git``. The
``etc/kolla/kolla-build.conf`` looks like:

::

    [glance-base]
    type = url
    location = http://tarballs.openstack.org/glance/glance-master.tar.gz

    [keystone]
    type = git
    location = https://github.com/openstack/keystone
    reference = stable/kilo

To build RHEL containers, it is necessary to use the -i (include header)
feature to include registration with RHN of the container runtime operating
system.  To obtain a RHN username/password/pool id, contact Red Hat.

First create a file called rhel-include:

::

    RUN subscription-manager register --user=<user-name> --password=<password> \
    && subscription-manager attach --pool <pool-id>

Then build RHEL containers:

::

    build -b rhel -i ./rhel-include



Known issues
------------


1. Can't build base image because docker fails to install systemd.


   There are some issue between docker and AUFS. The simple workaround
   to avoid the issue is that add ``-s devicemapper`` to ``DOCKER_OPTS``.
   Get more information about the issue from DockerBug_.


Docker Local Registry
---------------------

It is recommended to set up local registry for Kolla developers
or deploying multinode. The reason using a local registry is
deployment performance will operate at local network speeds,
typically gigabit networking. Beyond performance considerations,
the Operator would have full control over images that are deployed.
If there is no local registry, nodes pull images from Docker Hub
when images are not found in local caches.

Setting up Docker Local Registry
++++++++++++++++++++++++++++++++

Running Docker registry is easy. Just use the following command:

::

   docker run -d -p 4000:5000 --restart=always --name registry registry

The default port of Docker registry is 5000.
But the 5000 port is also the port of keystone-api.
To avoid conflict, use 4000 port as Docker registry port.

Now the Docker registry service is running.

Docker Insecure Registry Config
+++++++++++++++++++++++++++++++

For docker to pull images, it is necessary to
modify the Docker configuration. The guide assumes that
the IP of the machine running Docker registry is 172.22.2.81.

In Ubuntu, add ``--insecure-registry 172.22.2.81:4000``
to ``DOCKER_OPTS`` in ``/etc/default/docker``.

In CentOS, uncomment ``INSECURE_REGISTRY`` and set ``INSECURE_REGISTRY``
to ``--insecure-registry 172.22.2.81:4000`` in ``/etc/sysconfig/docker``.

And restart the docker service.

To build and push images to local registry, use the following command:

::

    tools/build.py --namespace 172.22.2.81:4000/kollaglue --push

Kolla-ansible with Local Registry
+++++++++++++++++++++++++++++++++

To make kolla-ansible pull images from local registry, set
``"docker_registry"`` to ``"172.22.2.81:4000"`` in
``"/etc/kolla/globals.yml"``. Make sure Docker is allowed to pull
images from insecure registry. See
`Docker Insecure Registry Config`_.


.. _DockerBug: https://github.com/docker/docker/issues/6980
