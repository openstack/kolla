.. _kolla_api:

================
Kolla Images API
================

Kolla offers two different ways to make changes to containers at runtime.
The first is via a :ref:`configuration file <kolla_api_external_config>`
exposed to the container and processed by the init scripts, and the second
is via more traditional
:ref:`environment variables <kolla_api_environment_variables>`.

.. _kolla_api_external_config:

External Config
===============

All of the Kolla images understand a JSON-formatted configuration
describing a set of actions the container needs to perform at runtime before it
executes the (potentially) long running process. This configuration also
specifies the command to execute to run the service.

When a container runs `kolla_start`_, the default entry-point, it processes
the configuration file using `kolla_set_configs`_ with escalated privileges,
meaning it is able to set file ownership and permissions.

.. _kolla_start: https://github.com/openstack/kolla/blob/master/docker/base/start.sh
.. _kolla_set_configs: https://github.com/openstack/kolla/blob/master/docker/base/set_configs.py

Format of the configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `kolla_set_configs`_ script understands the following attributes:

* **command** (required): the command the container runs once it finishes the
  initialization step.
* **config_files**: copies files and directories inside the container. A list
  of dicts, each containing the following attributes:

  * **source** (required): path to the file or directory that needs to be
    copied. Understands shell wildcards.
  * **dest** (required): path to where the file or directory will be copied.
    does not need to exist, destination is deleted if it exists.
  * **owner** (required, unless ``preserve_properties`` is set to true): the
    ``user:group`` to change ownership to. ``user`` is synonymous to
    ``user:user``. Must be user and group names, not uid/gid.
  * **perm** (required, unless `preserve_properties` is set to true): the unix
    permissions to set to the target files and directories. Must be passed in
    the numeric octal form.
  * **preserve_properties**: copies the ownership and permissions from the
    original files and directory. Boolean, defaults to ``false``.
  * **optional**: do not raise an error when the source file is not present on
    the filesystem. Boolean, defaults to ``false``.
  * **merge**: merges the source directory into the target directory instead of
    replacing it. Boolean, defaults to ``false``.

* **permissions**: change the permissions and/or ownership of files or
  directories inside the container. A list of dicts, each containing the
  following attributes:

  * **path** (required): the path to the file or directory to update.
  * **owner** (required): the ``user:group`` to change ownership to. ``user``
    is synonymous to ``user:user``. Must be user and group names, not uid/gid.
  * **perm**: the unix permissions to set to the target files and directories.
    Must be passed in the numeric octal form.
  * **recurse**: whether to apply the change recursively over the target
    directory. Boolean, defaults to ``false``.
  * **exclude**: array of names of the directories or files to be excluded when
    ``recurse`` is set to ``true``. Supports Python regular expressions.
    Defaults to empty array.

Here is an example configuration file:

.. code-block:: json

    {
        "command": "trove-api --config-file=/etc/trove/trove.conf",
        "config_files": [
            {
                "source": "/var/lib/kolla/config_files/trove.conf",
                "dest": "/etc/trove/trove.conf",
                "owner": "trove",
                "perm": "0600",
                "optional": false
            }
        ],
        "permissions": [
            {
                "path": "/var/log/kolla/trove",
                "owner": "trove:trove",
                "recurse": true,
                "exclude": ["/var/log/^snapshot.*"]
            }
        ]
    }

Passing the configuration file to the container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration to the container can be passed through a dedicated path:
``/var/lib/kolla/config_files/config.json``.
It is advised to ensure this path is mounted read-only for security reasons.

Mounting the configuration file in the container:

.. code-block:: console

   docker run -e KOLLA_CONFIG_STRATEGY=COPY_ALWAYS \
       -v /path/to/config.json:/var/lib/kolla/config_files/config.json:ro \
       kolla-image

.. _kolla_api_environment_variables:

Environment Variables
=====================

Variables to pass to the containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Kolla containers also understand some environment variables to change their
behavior at runtime:

* **KOLLA_CONFIG_STRATEGY** (required): Defines how the :ref:`kolla_start
  script <kolla_api_external_config>` copies the configuration file. Must be
  one of:

  * **COPY_ONCE**: the configuration files are copied just once, the first time
    the container is started. In this scenario the container is perfectly
    immutable.
  * **COPY_ALWAYS**: the configuration files are copied each time the container
    starts. If a config file changes on the host, the change is applied in the
    container the next time it restarts.

* **KOLLA_SKIP_EXTEND_START**: if set, bypass the ``extend_start.sh`` script.
  Not set by default.
* **KOLLA_SERVICE_NAME**: if set, shows the value of the variable on the
  ``PS1`` inside the container. Not set by default.
* **KOLLA_BOOTSTRAP**: if set, and supported by the image, runs the bootstrap
  code defined in the images ``extend_start.sh`` scripts. Not set by default.
* **KOLLA_UPGRADE**: if set, and supported by the image, runs the upgrade code
  defined in the images ``extend_start.sh`` scripts. Not set by default.
* **KOLLA_UPGRADE_CHECK**: if set, and supported by the image, runs the
  ``<service>-status upgrade check`` command, defined in the images
  ``extend_start.sh`` scripts. Currently, this is hard-coded to just
  ``nova-status upgrade check``. Not set by default.
* **KOLLA_OSM**: if set, and supported by the image, runs the online database
  migration code defined in the images ``extend_start.sh`` scripts. Not set by
  default.

The containers may expose other environment variables for turning features on
or off, such as the horizon container that looks for ``ENABLE_XXX`` variables
where ``XXX`` is a horizon plugin name. These are generally defined in the
container-specific ``extend_start.sh`` script, example for `horizon`_.

.. _horizon: https://github.com/openstack/kolla/blob/master/docker/horizon/extend_start.sh

Variables available in the containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following variables available in all images and can be evaluated in
scripts:

* **KOLLA_BASE_DISTRO**: ``base_distro`` used to build the image (e.g. centos,
  ubuntu)
