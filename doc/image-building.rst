.. _image-building:

=========================
Building Container Images
=========================

The ``kolla-build`` command is responsible for building Docker images.

.. note::

  When developing Kolla it can be useful to build images using files located in
  a local copy of Kolla. Use the ``tools/build.py`` script instead of
  ``kolla-build`` command in all below instructions.

Generating kolla-build.conf
===========================

Install tox and generate the build configuration. The build configuration is
designed to hold advanced customizations when building containers.

Create kolla-build.conf using the following steps.

::

    pip install tox
    tox -e genconfig

The location of the generated configuration file is
``etc/kolla/kolla-build.conf``, it can also be copied to ``/etc/kolla``. The
default location is one of ``/etc/kolla/kolla-build.conf`` or
``etc/kolla/kolla-build.conf``.

Guide
=====

In general, images are built like this::

    kolla-build

By default, the above command would build all images based on CentOS image.

The operator can change the base distro with the ``-b`` option::

    kolla-build -b ubuntu

There are following distros available for building images:

- centos
- oraclelinux
- ubuntu

.. warning::

   Fedora images are deprecated since Newton and will be removed
   in the future.

It is possible to build only a subset of images by specifying them on the
command line::

    kolla-build keystone

In this case, the build script builds all images which name contains the
``keystone`` string along with their dependencies.

Multiple names may be specified on the command line::

    kolla-build keystone nova

The set of images built can be defined as a profile in the ``profiles`` section
of ``kolla-build.conf``. Later, profile can be specified by ``--profile`` CLI
argument or ``profile`` option in ``kolla-build.conf``. Kolla provides some
pre-defined profiles:

- ``infra`` infrastructure-related images
- ``main`` core OpenStack images
- ``aux`` auxiliary images such as trove, magnum, ironic
- ``default`` minimal set of images for a working deploy

For example, due to Magnum requires Heat, following profile can be add to
``profiles`` section in ``kolla-build.conf`` ::

    magnum = magnum,heat

These images can be built using command line ::

    kolla-build --profile magnum

Or put following line to ``DEFAULT`` section in ``kolla-build.conf`` ::

    profile = magnum


``kolla-build`` uses ``kolla`` as default Docker namespace. This is
controlled with the ``-n`` command line option. To push images to a Dockerhub
repository named ``mykollarepo``::

    kolla-build -n mykollarepo --push

To push images to a :ref:`local registry<deploy_a_registry>`, use
``--registry`` flag::

    kolla-build --registry 172.22.2.81:5000 --push

The build configuration can be customized using a config file, the default
location being one of ``/etc/kolla/kolla-build.conf`` or
``etc/kolla/kolla-build.conf``. This file can be generated using the following
command::

    tox -e genconfig

Build OpenStack from source
===========================

When building images, there are two methods of the OpenStack install. One is
``binary``. Another is ``source``. The ``binary`` means that OpenStack will be
installed from apt/yum. And the ``source`` means that OpenStack will be
installed from source code. The default method of the OpenStack install is
``binary``. It can be changed to ``source`` using the ``-t`` option::

    kolla-build -t source

The locations of OpenStack source code are written in
``etc/kolla/kolla-build.conf``.
Now the source type supports ``url``, ``git``, and ``local``. The location of
the ``local`` source type can point to either a directory containing the source
code or to a tarball of the source. The ``local`` source type permits to make
the best use of the Docker cache.

``etc/kolla/kolla-build.conf`` looks like::

    [glance-base]
    type = url
    location = http://tarballs.openstack.org/glance/glance-master.tar.gz

    [keystone]
    type = git
    location = https://git.openstack.org/openstack/keystone
    reference = stable/mitaka

    [heat-base]
    type = local
    location = /home/kolla/src/heat

    [ironic-base]
    type = local
    location = /tmp/ironic.tar.gz

To build RHEL containers, it is necessary to include registration with RHN
of the container runtime operating system.  To obtain a RHN
username/password/pool id, contact Red Hat.  Use a template's header block
overrides file, add the following::

    RUN subscription-manager register --user=<user-name> \
    --password=<password> && subscription-manager attach --pool <pool-id>

Dockerfile Customisation
========================

As of the Newton release, the ``kolla-build`` tool provides a Jinja2 based
mechanism which allows operators to customise the Dockerfiles used to generate
Kolla images.

This offers a lot of flexibility on how images are built, e.g. installing extra
packages as part of the build, tweaking settings, installing plugins, and
numerous other capabilities. Some of these examples are described in more
detail below.

Generic Customisation
---------------------

Anywhere the line ``{% block ... %}`` appears may be modified. The Kolla
community have added blocks throughout the Dockerfiles where we think they will
be useful, however, operators are free to submit more if the ones provided are
inadequate.

The following is an example of how an operator would modify the setup steps
within the Horizon Dockerfile.

First, create a file to contain the customisations, e.g.
``template-overrides.j2``. In this place the following::

    {% extends parent_template %}

    # Horizon
    {% block horizon_redhat_binary_setup %}
    RUN useradd --user-group myuser
    {% endblock %}

Then rebuild the horizon image, passing the ``--template-override`` argument::

    kolla-build --template-override template-overrides.j2 horizon

.. note::

    The above example will replace all contents from the original block. Hence
    in many cases one may want to copy the original contents of the block before
    making changes.

    More specific functionality such as removing/appending entries is available
    for packages, described in the next section.

Package Customisation
---------------------

Packages installed as part of a container build can be overridden, appended to,
and deleted. Taking the Horizon example, the following packages are installed
as part of a binary install type build:

* ``openstack-dashboard``
* ``httpd``
* ``mod_wsgi``
* ``gettext``

To add a package to this list, say, ``iproute``, first create a file, e.g.
``template-overrides.j2``. In this place the following::

    {% extends parent_template %}

    # Horizon
    {% set horizon_packages_append = ['iproute'] %}

Then rebuild the horizon image, passing the ``--template-override`` argument:

    kolla-build --template-override template-overrides.j2 horizon

Alternatively ``template_override`` can be set in ``kolla-build.conf``.

The ``append`` suffix in the above example carries special significance. It
indicates the operation taken on the package list. The following is a complete
list of operations available:

override
    Replace the default packages with a custom list.

append
    Add a package to the default list.

remove
    Remove a package from the default list.

Using a different base image
----------------------------

Base-image can be specified by argument ``--base-image``. For example::

    kolla-build --base-image registry.access.redhat.com/rhel7/rhel --base rhel


Plugin Functionality
--------------------

The Dockerfile customisation mechanism is also useful for adding/installing
plugins to services. An example of this is Neutron's third party L2 drivers_.

The bottom of each Dockerfile contains two blocks, ``image_name_footer``, and
``footer``. The ``image_name_footer`` is intended for image specific
modifications, while the ``footer`` can be used to apply a common set of
modifications to every Dockerfile.

For example, to add the ``networking-cisco`` plugin to the ``neutron_server``
image, add the following to the ``template-override`` file::

    {% extends parent_template %}

    {% block neutron_server_footer %}
    RUN git clone https://git.openstack.org/openstack/networking-cisco \
        && pip --no-cache-dir install networking-cisco
    {% endblock %}

Acute readers may notice there is one problem with this however. Assuming
nothing else in the Dockerfile changes for a period of time, the above ``RUN``
statement will be cached by Docker, meaning new commits added to the Git
repository may be missed on subsequent builds. To solve this the Kolla build
tool also supports cloning additional repositories at build time, which will be
automatically made available to the build, within an archive named
``plugins-archive``.

.. note::

    The following is available for source build types only.

To use this, add a section to ``/etc/kolla/kolla-build.conf`` in the following
format::

    [<image>-plugin-<plugin-name>]

Where ``<image>`` is the image that the plugin should be installed into, and
``<plugin-name>`` is the chosen plugin identifier.

Continuing with the above example, add the following to
``/etc/kolla/kolla-build.conf``::

    [neutron-server-plugin-networking-cisco]
    type = git
    location = https://git.openstack.org/openstack/networking-cisco
    reference = master

The build will clone the repository, resulting in the following archive
structure::

    plugins-archive.tar
    |__ plugins
        |__networking-cisco

The template now becomes::

    {% block neutron_server_footer %}
    ADD plugins-archive /
    pip --no-cache-dir install /plugins/*
    {% endblock %}

Custom Repos
------------

Red Hat
-------
The build method allows the operator to build containers from custom repos.
The repos are accepted as a list of comma separated values and can be in the
form of ``.repo``, ``.rpm``, or a url. See examples below.

Update ``rpm_setup_config`` in ``/etc/kolla/kolla-build.conf``::

    rpm_setup_config = http://trunk.rdoproject.org/centos7/currrent/delorean.repo,http://trunk.rdoproject.org/centos7/delorean-deps.repo

If specifying a ``.repo`` file, each ``.repo`` file will need to exist in the
same directory as the base Dockerfile (``kolla/docker/base``)::

    rpm_setup_config = epel.repo,delorean.repo,delorean-deps.repo

Ubuntu
------
For Debian based images, additional apt sources may be added to the build as
follows::

    apt_sources_list = custom.list

Known issues
============

#. Can't build base image because Docker fails to install systemd or httpd.

   There are some issues between Docker and AUFS. The simple workaround to
   avoid the issue is that add ``-s devicemapper`` or ``-s btrfs`` to
   ``DOCKER_OPTS``. Get more information about `the issue from the Docker bug
   tracker <https://github.com/docker/docker/issues/6980>`_ and `how to
   configure Docker with BTRFS back end <https://docs.docker.com/engine/userguide/storagedriver/btrfs-driver/#prerequisites>`_.

#. Mirrors are unreliable.

   Some of the mirrors Kolla uses can be unreliable. As a result occasionally
   some containers fail to build. To rectify build problems, the build tool
   will automatically attempt three retries of a build operation if the first
   one fails. The retry count is modified with the ``--retries`` option.

Kolla-ansible with Local Registry
---------------------------------

To make kolla-ansible pull images from a local registry, set
``"docker_registry"`` to ``"172.22.2.81:5000"`` in
``"/etc/kolla/globals.yml"``. Make sure Docker is allowed to pull images from
insecure registry. See
:ref:`Docker Insecure Registry Config <deploy_a_registry>`.

Building behind a proxy
-----------------------

We can insert http_proxy settings into the images to
fetch packages during build, and then unset them at the end to avoid having
them carry through to the environment of the final images. Note however, it's
not possible to drop the info completely using this method; it will still be
visible in the layers of the image.

To set the proxy settings, we can add this to the template's header block::

    ENV http_proxy=https://evil.corp.proxy:80
    ENV https_proxy=https://evil.corp.proxy:80

To unset the proxy settings, we can add this to the template's footer block::

    ENV http_proxy=""
    ENV https_proxy=""

Besides this configuration options, the script will automatically read these
environment variables. If the host system proxy parameters match the ones
going to be used, no other input parameters will be needed. These are the
variables that will be picked up from the user env::

    HTTP_PROXY, http_proxy, HTTPS_PROXY, https_proxy, FTP_PROXY,
    ftp_proxy, NO_PROXY, no_proxy

Also these variables could be overwritten using ``--build-args``, which have
precedence.

.. _drivers: https://wiki.openstack.org/wiki/Neutron#Plugins
