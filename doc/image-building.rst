Building Container Images
=========================

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

To push images to local registry, use ``--registry`` flag like the
following command:

::

    tools/build.py --registry 172.22.2.81:4000 --push

To trigger build.py to pull images from local registry,
the Docker configuration needs to be modified. See
`Docker Insecure Registry Config`_.

The build configuration can be customised using a config file, the default
location being one of ``/etc/kolla/kolla-build.conf`` or
``etc/kolla/kolla-build.conf``. This file can be generated using the following
command:

::

    tox -e genconfig


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
Now the source type supports ``url``, ``git``, and ``local``. The location of
the ``local`` source type can point to either a directory containing the source
code or to a tarball of the source. The ``local`` source type permits to make
the best use of the docker cache.

``etc/kolla/kolla-build.conf`` looks like:

::

    [glance-base]
    type = url
    location = http://tarballs.openstack.org/glance/glance-master.tar.gz

    [keystone]
    type = git
    location = https://github.com/openstack/keystone
    reference = stable/kilo

    [heat-base]
    type = local
    location = /home/kolla/src/heat

    [ironic-base]
    type = local
    location = /tmp/ironic.tar.gz

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



Plugin Functionality
--------------------

.. note::

  The following functionality currently exists only for Neutron. Other
  services will be made pluggable in Kolla in the near future.

  Plugin functionality is available for the source build type only.

Certain OpenStack services support third party plugins, e.g. Neutron's
pluggable L2 drivers_.

Kolla supports downloading pip installable archives as part of the build, which
will then be picked up and installed in the relevant image.

To instruct Kolla to use these, add a section to
``/etc/kolla/kolla-build.conf`` in the following format:

::

    [<image>-plugin-<plugin-name>]

Where, ``<image>`` is the image that the plugin should be installed into, and
``<plugin-name>`` is an identifier of your choice.

For example, to install the Cisco L2 plugin for Neutron into the neutron-server
image, one would add the following block to ``/etc/kolla/kolla-build.conf``:

::

    [neutron-server-plugin-networking-cisco]
    type = git
    location = https://github.com/openstack/networking-cisco
    reference = master


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

    tools/build.py --registry 172.22.2.81:4000 --push

Kolla-ansible with Local Registry
+++++++++++++++++++++++++++++++++

To make kolla-ansible pull images from local registry, set
``"docker_registry"`` to ``"172.22.2.81:4000"`` in
``"/etc/kolla/globals.yml"``. Make sure Docker is allowed to pull
images from insecure registry. See
`Docker Insecure Registry Config`_.


Building behind a proxy
+++++++++++++++++++++++

The build script supports augmenting the Dockerfiles under build via so called
`header` and `footer` files.  Statements in the `header` file are included at
the top of the `base` image, while those in `footer` are included at the bottom
of every Dockerfile in the build.

A common use case for this is to insert http_proxy settings into the images to
fetch packages during build, and then unset them at the end to avoid having
them carry through to the environment of the final images. Note however, it's
not possible to drop the info completely using this method; it will still be
visible in the layers of the image.

To use this feature, create a file called ``.header``, with the following
content for example:

::

    ENV http_proxy=https://evil.corp.proxy:80
    ENV https_proxy=https://evil.corp.proxy:80

Then create another file called ``.footer``, with the following content:

::

    ENV http_proxy=""
    ENV https_proxy=""

Finally, pass them to the build script using the ``-i`` and ``-I`` flags:

::

    tools/build.py -i .header -I .footer

Besides this configuration options, the script will automatically read these
environment variables. If the host system proxy parameters match the ones
going to be used, no other input parameters will be needed. These are the
variables that will be picked up from the user env:

::

    HTTP_PROXY, http_proxy, HTTPS_PROXY, https_proxy, FTP_PROXY,
    ftp_proxy, NO_PROXY, no_proxy

Also these variables could be overwritten using ``--build-args``, which have
precedence.

.. _DockerBug: https://github.com/docker/docker/issues/6980
.. _drivers: https://wiki.openstack.org/wiki/Neutron#Plugins
