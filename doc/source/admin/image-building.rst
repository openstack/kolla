=========================
Building Container Images
=========================

Firstly, ensure ``kolla`` and the container engine of your choice is installed.

Currently supported container engines are ``docker`` and ``podman``.

.. code-block:: console

   python3 -m pip install kolla
   #only one of these is needed:
   python3 -m pip install podman
   python3 -m pip install docker

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

The locations of OpenStack source code are written in ``kolla-build.conf``.
The source's ``type`` supports ``url``, ``git`` and ``local``. The
``location`` of the ``local`` source type can point to either a directory
containing the source code or to a tarball of the source. The ``local`` source
type permits to make the best use of the Docker cache.  A source may be
disabled by setting ``enabled`` to ``False``.

The ``kolla-build.conf`` file could look like this:

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [horizon]
   type = url
   location = https://tarballs.openstack.org/horizon/horizon-master.tar.gz

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
   enabled = False

.. note::

   Note that the name of the section should exactly match the image name
   you are trying to change source location for.

If using the ``local`` source type, the ``--locals-base`` flag can be used to
define a path prefix, which you can reference in the config.

.. path etc/kolla/kolla-build.conf
.. code-block:: ini

  [DEFAULTS]
  locals_base = /home/kolla/src

  [heat-base]
  type = local
  location = $locals_base/heat

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
   {% block horizon_ubuntu_source_setup %}
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
as part of a package install (among others):

* ``gettext``
* ``locales``

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

To remove a package from that list, say ``locales``, one would do:

.. code-block:: jinja

   {% extends parent_template %}

   # Horizon
   {% set horizon_packages_remove = ['locales'] %}

An example of this is the Grafana plugins, which are mentioned in the next
section.

Grafana plugins
^^^^^^^^^^^^^^^

Additional Grafana plugins can be installed by adding the plugin name to the
``grafana_plugins_append`` list. Plugins can also be removed by adding the
plugin name to the ``grafana_plugins_remove`` list. Additionally the entire
list can be overridden by setting the ``grafana_plugins_override`` variable.

.. code-block:: ini

   grafana_plugins_append:
      - grafana-piechart-panel
      - vonage-status-panel

Patching customization
----------------------

Kolla provides functionality to apply patches to Docker images during the build
process. This allows users to modify existing files or add new ones as part of
the image creation.

You need to define a ``patches_path`` in the ``[DEFAULT]`` section of
the ``/etc/kolla/kolla-build.conf`` file. This directory will be used to store
patches for the images.

.. path etc/kolla/kolla-build.conf
.. code-block:: ini

  [DEFAULT]
  patches_path = /path/to/your/patches

Create a directory for each image you want to patch, following a directory
structure similar to the Debian patch quilt format. Refer to
`quilt documentation <https://linux.die.net/man/1/quilt>`_. for more details.

- ``<patches_path>/image_name/`` : The directory for the specific image.
- ``<patches_path>/image_name/some-patch`` : Contains the patch content.
- ``<patches_path>/image_name/another-patch`` : Contains the patch content.
- ``<patches_path>/image_name/series`` : Lists the order in which the patches
  will be applied.

For example, if you want to patch the ``nova-api`` image, the structure would
look like this:

.. code-block:: console

   /path/to/your/patches/nova-api/some-patch
   /path/to/your/patches/nova-api/another-patch
   /path/to/your/patches/nova-api/series

The ``series`` file should list the patches in the order they should be
applied:

.. code-block:: console

   some-patch
   another-patch

When the images are built using ``kolla-build``, the patches defined in the
``patches_path`` will automatically be applied to the corresponding images.

After the patches are applied, Kolla stores information about the applied
patches in ``/etc/kolla/patched``. The patch files themselves are stored
in the ``/patches`` directory within the image. This allows you to track
which patches have been applied to each image for debugging or
verification purposes.

Python packages build options
-----------------------------

The block ``base_pip_conf`` in the ``base`` Dockerfile can be used to provide
the PyPI build customisation options via the standard environment variables
like ``PIP_INDEX_URL``, ``PIP_TRUSTED_HOST``, etc.

To override PYPI upper-constraints of all OpenStack images, you can
define the source location of openstack-base. in ``kolla-build.conf``.

Upstream repository of `openstack-base (requirements) <https://opendev.org/openstack/requirements>`__
has a source of
`upper constraints file <https://opendev.org/openstack/requirements/src/branch/master/upper-constraints.txt>`__.

Make a fork or clone the repository then customise ``upper-constraints.txt``
and define the location of ``openstack-base`` in ``kolla_build.conf``.

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   # These examples use upstream openstack-base as a demonstration
   # To use custom openstack-base, make changes accordingly

   # Using git source
   [openstack-base]
   type = git
   location = https://opendev.org/openstack/requirements
   reference = master

   # Using URL source
   [openstack-base]
   type = url
   location = https://tarballs.opendev.org/openstack/requirements/requirements-master.tar.gz

   # Using local source
   [openstack-base]
   type = local
   location = /home/kolla/src/requirements

To remove or change the version of specific Python packages in
``openstack-base`` upper-constraints, you can use the block
``openstack_base_override_upper_constraints`` in your template file,
for example, ``template-overrides.j2``:

.. code-block:: jinja

   {% block openstack_base_override_upper_constraints %}
   RUN {{ macros.upper_constraints_version_change("sqlparse", "0.4.4", "0.5.0") }}
   RUN {{ macros.upper_constraints_remove("reno") }}
   {% endblock %}

``kolla-toolbox`` image needs different approach as it does not uses
``openstack-base`` as a base image.
A variable ``UPPER_CONSTRAINTS_FILE`` is set in the
Dockerfile of ``kolla-toolbox``.
To change variable, add the following contents to the
``kolla_toolbox_pip_conf`` block in your template file, for example,
``template-overrides.j2``:

.. code-block:: jinja

   {% block kolla_toolbox_pip_conf %}
   ENV UPPER_CONSTRAINTS_FILE=https://releases.openstack.org/constraints/upper/master
   {% endblock %}

.. note::

   ``UPPER_CONSTRAINTS_FILE`` must be a valid URL to the file

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

Some plugins are installed by default. For images with default plugins, the
Dockerfiles already copy the ``plugins-archive`` to the image and install
available plugins at build time. These default plugins may be disabled by
setting ``enabled`` to ``False`` in the relevant plugin source configuration
section in ``kolla-build.conf``.

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

The template becomes now:

.. code-block:: jinja

   {% block neutron_server_footer %}
   ADD additions-archive /
   RUN cp /additions/jenkins/jenkins.json /jenkins.json
   {% endblock %}

Custom docker templates
-----------------------

In order to unify the process of managing OpenStack-related projects, Kolla
provides a way of building images for external 'non-built-in' projects.

If the template for a 'non-built-in' project meets Kolla template standards,
an operator can provide a root directory with a template via the
``--docker-dir`` CLI option (can be specified multiple times).

All Kolla's jinja2 macros should be available the same as for built-in
projects with some notes:

- The ``configure_user`` macro. As the 'non-built-in' user is unknown to Kolla,
  there are no default values for user ID and group ID to use.
  To use this macro, an operator should specify "non-default" user details
  with ``<custom_user_name>-user`` configuration section and include info
  for ``uid`` and ``gid`` at least.

Let's look into how an operator can build an image for an in-house project
with Kolla using `openstack/releases <https://opendev.org/openstack/releases>`_
project.

First, create a ``Dockerfile.j2`` template for the project.

.. path /home/kolla/custom-kolla-docker-templates/releaser/Dockerfile.j2
.. code-block:: jinja

   FROM {{ namespace }}/{{ image_prefix }}openstack-base:{{ tag }}

   {% block labels %}
   LABEL maintainer="{{ maintainer }}" name="{{ image_name }}" build-date="{{ build_date }}"
   {% endblock %}

   {% block releaser_header %}{% endblock %}

   {% import "macros.j2" as macros with context %}

   {{ macros.configure_user(name='releaser') }}

   RUN ln -s releaser-source/* /releaser \
       && {{ macros.install_pip(['/releaser-source']  | customizable("pip_packages")) }} \
       && mkdir -p /etc/releaser \
       && chown -R releaser: /etc/releaser \
       && chmod 750 /etc/sudoers.d \
       && touch /usr/local/bin/kolla_releaser_extend_start \
       && chmod 644 /usr/local/bin/kolla_extend_start /usr/local/bin/kolla_releaser_extend_start

   {% block footer %}{% endblock %}

Suggested directory structure:

.. code-block:: console

   custom-kolla-docker-templates
   |__ releaser
       |__ Dockerfile.j2

Then, modify Kolla's configuration so the engine can download sources and
configure users.

.. path /etc/kolla/kolla-build.conf
.. code-block:: ini

   [releaser]
   type = git
   location = https://opendev.org/openstack/releases
   reference = master

   [releaser-user]
   uid = 53001
   gid = 53001

Last pre-check before building a new image - ensure that the new template
is visible for Kolla:

.. code-block:: console

   $ kolla-build --list-images --docker-dir custom-kolla-docker-templates "^releaser$"
   1 : base
   2 : releaser
   3 : openstack-base

And finally, build the ``releaser`` image, passing the ``--docker-dir``
argument:

.. code-block:: console

   kolla-build --docker-dir custom-kolla-docker-templates "^releaser$"

Can I use the ``--template-override`` option for custom templates? Yes!

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

Cross-compiling
---------------

It is possible to cross-compile container images in order to, e.g., build
``aarch64`` images on a ``x86_64`` machine.

To build ``ARM`` images on ``x86_64`` platform, pass the ``--base-arch`` and
``--platform`` arguments:

.. code-block:: console

   kolla-build --platform linux/arm64 --base-arch aarch64

.. note::

   To make this work on x86_64 platform you can use tools like: `qemu-user-static
   <https://github.com/multiarch/qemu-user-static>`_ or `binfmt
   <https://github.com/tonistiigi/binfmt>`_.

   To make this work on Apple Silicon you can use Docker Desktop or Podman
   Desktop to build ``x86_64`` or native ``ARM`` images.

Known issues
============

#. Mirrors are unreliable.

   Some of the mirrors Kolla uses can be unreliable. As a result occasionally
   some containers fail to build. To rectify build problems, the build tool
   will automatically attempt three retries of a build operation if the first
   one fails. The retry count is modified with the ``--retries`` option.
