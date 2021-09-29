=========================
Building Container Images
=========================

Firstly, ensure ``kolla`` is installed.

.. code-block:: console

   python3 -m pip install kolla

Then, the :command:`kolla-build` command is available for building
Docker images.

Building kolla images
=====================

In general, images are built like this:

.. code-block:: console

   kolla-build

By default, the above command would build all images based on a CentOS Stream
image.

The operator can change the base distro with the ``-b`` option:

.. code-block:: console

   kolla-build -b ubuntu

There are following distros (bases) available for building images:

- centos
- debian
- ubuntu

See the :ref:`support matrix <support-matrix-base-images>` for information on
supported base image distribution versions and supported images on each
distribution.

It is possible to build only a subset of images by specifying them on the
command line:

.. code-block:: console

   kolla-build keystone

In this case, the build script builds all images whose name contains the
``keystone`` string, along with their parents.

Multiple names may be specified on the command line:

.. code-block:: console

   kolla-build keystone nova

Each string is actually a regular expression so one can do:

.. code-block:: console

   kolla-build ^nova-

``kolla-build`` can be configured via an INI file, canonically named
``kolla-build.conf`` and placed in ``/etc/kolla``. A custom path to it can be
set via the ``--config-file`` argument. Most CLI arguments can be set via this
config file. Remember to convert the names from hyphenated to underscored.
Run ``kolla-build --help`` to see all available options.

The set of images to build can be defined as a profile in the ``profiles``
section of ``kolla-build.conf``.
Then, profile can be specified by ``--profile`` CLI argument or ``profile``
option in ``kolla-build.conf``.

For example, since Magnum requires Heat, one could add the following profile to
``profiles`` section in ``kolla-build.conf``:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [profiles]
   magnum = magnum,heat

These images could then be built using command line:

.. code-block:: console

   kolla-build --profile magnum

Or putting the following line in the ``DEFAULT`` section in
``kolla-build.conf`` file:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [DEFAULT]
   profile = magnum

The :command:`kolla-build` uses ``kolla`` as default Docker namespace. This is
controlled with the ``-n`` command line option. To push images to a Dockerhub
repository named ``mykollarepo``:

.. code-block:: console

   kolla-build -n mykollarepo --push

To push images to a :kolla-ansible-doc:`local registry
<user/multinode.html#deploy-a-registry>`, use the ``--registry`` flag:

.. code-block:: console

   kolla-build --registry 172.22.2.81:4000 --push

Build OpenStack from source
===========================

When building images, there are two methods of the OpenStack install. One is
``binary``. Another is ``source``. The ``binary`` means that OpenStack will be
installed from apt/dnf. And the ``source`` means that OpenStack will be
installed from upstream sources. The default method of the OpenStack install is
``source``. It can be changed to ``binary`` using the ``-t`` option:

.. code-block:: console

   kolla-build -t binary

The locations of OpenStack source code are written in ``kolla-build.conf``.
The source type supports ``url``, ``git``, and ``local``. The location of
the ``local`` source type can point to either a directory containing the source
code or to a tarball of the source. The ``local`` source type permits to make
the best use of the Docker cache.

The ``kolla-build.conf`` file could look like this:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [glance-base]
   type = url
   location = https://tarballs.openstack.org/glance/glance-master.tar.gz

   [keystone-base]
   type = git
   location = https://opendev.org/openstack/keystone
   reference = stable/mitaka

   [heat-base]
   type = local
   location = /home/kolla/src/heat

   [ironic-base]
   type = local
   location = /tmp/ironic.tar.gz

.. _dockerfile-customisation:

Dockerfile customisation
========================

The ``kolla-build`` tool provides a Jinja2-based
mechanism which allows operators to customise the Dockerfiles used to generate
Kolla images.

This offers a lot of flexibility on how images are built, for example:
installing extra packages as part of the build, tweaking settings or installing
plugins. Examples of these are described in more detail below.

.. note::

   The Docker file Jinja2 template for each image is found in subdirectories
   of the ``docker`` directory included in the ``kolla`` package.

Using a different base image
----------------------------

Base image can be specified using ``--base-image``:

.. code-block:: console

   kolla-build --base-image <image-identifier>

The ``image-identifier`` accepts any format that Docker accepts when
referencing an image.

Generic customisation
---------------------

Kolla templates are designed such that each Docker file has logical sections
represented by Jinja2's named ``block`` section directives. These can be
overridden at will by Kolla users.
The following is an example of how an operator would modify the setup steps
within the Horizon Dockerfile.

First, create a file to contain the customisations, for example:
``template-overrides.j2``. Fill it with the following contents:

.. code-block:: jinja

   {% extends parent_template %}

   # Horizon
   {% block horizon_redhat_binary_setup %}
   RUN useradd --user-group myuser
   {% endblock %}

Then rebuild the ``horizon`` image, passing the ``--template-override``
argument:

.. code-block:: console

   kolla-build --template-override template-overrides.j2 ^horizon$

.. note::

   The above example will replace all contents of the original block. Hence,
   one may want to copy the original contents of the block before and modify it.
   Do note it makes the customisations ignore changes in Kolla upstream.

   We recommend users use more specific customisation functionalities, such
   as removing/appending entries for packages. These other customisations are
   described in the following sections.

Two block series are of particular interest and are safe to override as they
are empty by design.
The top of each Dockerfile includes ``<image_name>_header`` block which can
be used for early customisations, such as RHN registration described later.
The bottom of each Dockerfile includes ``<image_name>_footer`` block which
is intended for image-specific modifications.
Do note to use the underscored name of the image, i.e., replace dashes with
underscores.
All leaf Dockerfiles, i.e. those meant for direct consumption, additionally
have a ``footer`` block which is then guaranteed to exist once at the very
end of the image recipe chain.

Packages customisation
----------------------

Packages installed as part of an image build can be overridden, appended to,
and deleted. Taking the Horizon example, the following packages are installed
as part of a binary install type build (among others):

* ``openstack-dashboard``
* ``openstack-magnum-ui``

To add a package to this list, say, ``iproute``, first create a file,
for example, ``template-overrides.j2``. In it place the following:

.. code-block:: jinja

   {% extends parent_template %}

   # Horizon
   {% set horizon_packages_append = ['iproute'] %}

Then rebuild the ``horizon`` image, passing the ``--template-override``
argument:

.. code-block:: console

   kolla-build --template-override template-overrides.j2 ^horizon$

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

To remove a package from that list, say ``openstack-magnum-ui``, one would do:

.. code-block:: jinja

   {% extends parent_template %}

   # Horizon
   {% set horizon_packages_remove = ['openstack-magnum-ui'] %}

Plugin functionality
--------------------

The Dockerfile customisation mechanism is useful for adding/installing
plugins to services. An example of this is Neutron's third party L2 `drivers
<https://wiki.openstack.org/wiki/Neutron#Plugins>`_.

For example, to add the ``networking-cisco`` plugin to the ``neutron_server``
image, one may be tempted to add the following to the ``template-override``
file:

.. warning::

   Do NOT do the below. Read on for why.

.. code-block:: jinja

   {% extends parent_template %}

   {% block neutron_server_footer %}
   RUN git clone https://opendev.org/x/networking-cisco \
       && python3 -m pip --no-cache-dir install networking-cisco
   {% endblock %}

Some readers may notice there is one problem with this, however. Assuming
nothing else in the Dockerfile changes for a period of time, the above ``RUN``
statement will be cached by Docker, meaning new commits added to the Git
repository may be missed on subsequent builds. To solve this, the
``kolla-build`` tool also supports cloning additional repositories at build
time, which will be automatically made available to the build, within an
archive named ``plugins-archive``.

.. note::

   The following is available for source build types only.

To use this, add a section to ``kolla-build.conf`` in the following format:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [<image-name>-plugin-<plugin-name>]

Where ``<image-name>`` is the hyphenated name of the image that the plugin
should be installed into, and ``<plugin-name>`` is the chosen plugin
identifier.

Continuing with the above example, one could add the following to
``kolla-build.conf``:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [neutron-server-plugin-networking-cisco]
   type = git
   location = https://opendev.org/x/networking-cisco
   reference = master

The build will clone the repository, resulting in the following archive
structure:

.. code-block:: console

   plugins-archive.tar
   |__ plugins
       |__networking-cisco

The template now becomes:

.. code-block:: jinja

   {% block neutron_server_footer %}
   ADD plugins-archive /
   python3 -m pip --no-cache-dir install /plugins/*
   {% endblock %}

Many of the Dockerfiles already copy the ``plugins-archive`` to the image and
install available plugins at build time.

Neutron plugins
^^^^^^^^^^^^^^^

One example of a service with many available plugins is Neutron.
The ``neutron-base`` image Dockerfile has plugins archive copying and
installation enabled already.
In the ``contrib`` directory of Kolla (as available in the repository,
the tarball or the ``share`` directory of the installation target), there
is a ``neutron-plugins`` directory with examples of Neutron plugins
definitions.
Some of these plugins used to be enabled by default but, due to
their release characteristic, have been excluded from the default builds.
Please read the included ``README.rst`` to learn how to apply them.

Additions functionality
-----------------------

The Dockerfile customisation mechanism is useful for adding/installing
additions into images. An example of this is adding your jenkins job build
metadata (say, formatted into a jenkins.json file) into the image.

Similarly to the plugins mechanism, the Kolla build tool also supports cloning
additional repositories at build time, which will be automatically made
available to the build, within an archive named ``additions-archive``. The main
difference between ``plugins-archive`` and ``additions-archive`` is that
``plugins-archive`` is automatically copied in many images and processed to
install available plugins while ``additions-archive`` processing is left solely
to the Kolla user.

.. note::

   The following is available for source build types only.

To use this, add a section to ``kolla-build.conf`` in the following format:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [<image>-additions-<additions-name>]

Where ``<image-name>`` is the hyphenated name of the image that the additions
should be copied into, and ``<additions-name>`` is the chosen additions
identifier.

For example, one could add the following to ``kolla-build.conf`` file:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [neutron-server-additions-jenkins]
   type = local
   location = /path/to/your/jenkins/data

The build will copy the directory, resulting in the following archive
structure:

.. code-block:: console

   additions-archive.tar
   |__ additions
       |__jenkins

Alternatively, it is also possible to create an ``additions-archive.tar`` file
yourself bypasssing ``kolla-build.conf`` in order to work with binary build
type.

The template becomes now:

.. code-block:: jinja

   {% block neutron_server_footer %}
   ADD additions-archive /
   RUN cp /additions/jenkins/jenkins.json /jenkins.json
   {% endblock %}

Custom repos
------------

Red Hat
^^^^^^^

Kolla allows the operator to build containers using custom repos.
The repos are accepted as a list of comma separated values and can be in the
form of ``.repo``, ``.rpm``, or a url. See examples below.

To use current RDO packages (aka Delorean or DLRN), update ``rpm_setup_config``
in ``kolla-build.conf``:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   rpm_setup_config = https://trunk.rdoproject.org/centos8/current/delorean.repo,https://trunk.rdoproject.org/centos8/delorean-deps.repo

If specifying a ``.repo`` file, each ``.repo`` file will need to exist in the
same directory as the base Dockerfile (``kolla/docker/base``):

.. path kolla/docker/base
.. code-block:: ini

   rpm_setup_config = epel.repo,delorean.repo,delorean-deps.repo

Debian / Ubuntu
^^^^^^^^^^^^^^^

For Debian based images, additional apt sources may be added to the build as
follows:

.. code-block:: ini

   apt_sources_list = custom.list

Building behind a proxy
-----------------------

We can insert http_proxy settings into the images to
fetch packages during build, and then unset them at the end to avoid having
them carry through to the environment of the final images. Note, however, it's
not possible to drop the info completely using this method; it will still be
visible in the layers of the image.

To set the proxy settings, we can add this to the template's header block:

.. code-block:: docker

   ENV http_proxy=https://evil.corp.proxy:80
   ENV https_proxy=https://evil.corp.proxy:80

To unset the proxy settings, we can add this to the template's footer block:

.. code-block:: docker

   ENV http_proxy=""
   ENV https_proxy=""

Besides this configuration options, the script will automatically read these
environment variables. If the host system proxy parameters match the ones
going to be used, no other input parameters will be needed. These are the
variables that will be picked up from the user env:

.. code-block:: docker

   HTTP_PROXY, http_proxy, HTTPS_PROXY, https_proxy, FTP_PROXY,
   ftp_proxy, NO_PROXY, no_proxy

Also these variables could be overwritten using ``--build-args``, which have
precedence.

Known issues
============

#. Mirrors are unreliable.

   Some of the mirrors Kolla uses can be unreliable. As a result occasionally
   some containers fail to build. To rectify build problems, the build tool
   will automatically attempt three retries of a build operation if the first
   one fails. The retry count is modified with the ``--retries`` option.
