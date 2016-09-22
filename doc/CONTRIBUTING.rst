.. _CONTRIBUTING:

=================
How To Contribute
=================

Basics
======

#. Our source code is hosted on `OpenStack Kolla Git`_. Bugs should be filed on
   launchpad_.

#. Please follow OpenStack `Gerrit Workflow`_ to to contribute to Kolla.

#. Note the branch you're proposing changes to. ``master`` is the current focus
   of development. Kolla project has a strict policy of only allowing backports
   in ``stable/branch``, unless when not applicable. A bug in a
   ``stable/branch`` will first have to be fixed in ``master``.

#. Please file a launchpad_ blueprint for any significant code change and a bug
   for any significant bug fix or add a TrivialFix tag for simple changes.
   See how to reference a bug or a blueprint in the commit message here_

#. TrivialFix tags or bugs are not required for documentation changes.

.. _OpenStack Kolla Git: https://git.openstack.org/cgit/openstack/kolla/
.. _launchpad: https://bugs.launchpad.net/kolla
.. _here: https://wiki.openstack.org/wiki/GitCommitMessages

Development Environment
=======================

Please follow our `quickstart`_ to deploy your environment and test your
changes.

.. _quickstart: http://docs.openstack.org/developer/kolla/quickstart.html

Please use the existing sandbox repository, available at
https://git.openstack.org/cgit/openstack-dev/sandbox, for learning, understanding
and testing the `Gerrit Workflow`_.

.. _Gerrit Workflow: http://docs.openstack.org/infra/manual/developers.html#development-workflow

Adding a new service
====================

Kolla aims to both containerise and deploy all services within the OpenStack
"big tent". This is a constantly moving target as the ecosystem grows, so these
guidelines aim to help make adding a new service to Kolla a smooth experience.

The image
---------
Kolla follows Docker best practices
(https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/)
when designing and implementing services where at all possible.

We use ``jinja2`` templating syntax to help manage the volume and complexity
that comes with maintaining multiple Dockerfiles for multiple different base
operating systems.

Images should be created under the ``docker`` directory. OpenStack services
should inherit from the provided ``openstack-base`` image, while supporting and
infrastructure services (e.g. mongodb) should inherit from ``base``.

Services consisting of only one service should be placed in an image named the
same as that service, e.g. ``horizon``. Services that consist of multiple
processes generally use a base image and child images, e.g. ``glance-base``,
``glance-api``, and ``glance-registry``.

Jinja2 'blocks' are employed throughout the Dockerfile's to help operators
customise various stages of the build (refer to
http://docs.openstack.org/developer/kolla/image-building.html?highlight=override#dockerfile-customisation)

Some of these blocks are free form however, there are a subset that should be
common to every Dockerfile. The overall structure for a multi container service
is as follows::

    FROM {{ namespace }}/{{ image_prefix }}openstack-base:{{ tag }}
    MAINTAINER {{ maintainer }}

    {% import "macros.j2" as macros with context %}

    << binary specific steps >>

    << source specific steps >>

    << common steps >>

    {% block << service >>_footer %}{% endblock %}
    {% block footer %}{% endblock %}
    {{ include_footer }}

.. NOTE::
  The generic footer block ``{% block footer %}{% endblock %}`` should not be
  included in base images (e.g. glance-base).

  {{ include_footer }} is legacy and should not be included in new services, it
  is superseded by {% block footer %}{% endblock %}

Orchestration
-------------
As of the Newton release there are two main orchestration methods in existence
for Kolla, Ansible and Kubernetes. Ansible is the most mature and generally
regarded as the reference implementation.

When adding a role for a new service in Ansible, there are couple of patterns
that Kolla uses throughout that should be followed.

* The sample inventories

  Entries should be added for the service in each of
  ``ansible/inventory/multinode`` and ``ansible/inventory/all-in-one``.

* The playbook

  The main playbook that ties all roles together is in ``ansible/site.yml``,
  this should be updated with appropriate roles, tags, and conditions. Ensure
  also that supporting hosts such as haproxy are updated when necessary.

* The common role

  A ``common`` role exists which sets up logging, ``kolla-toolbox`` and other
  supporting components. This should be included in all services within
  ``meta/main.yml`` of your role.

* Common tasks

  All services should include the following tasks:

  - ``do_reconfigure.yml`` : Used to push new configuration files to the host and
    restart the service.

  - ``pull.yml`` : Used to pre fetch the image into the Docker image cache on hosts,
    to speed up intial deploys.

  - ``upgrade.yml`` : Used for upgrading the service in a rolling fashion. May
    include service specific setup and steps as not all services can be upgraded
    in the same way.

* Log delivery

  - For OpenStack services the service has be added oo the ``file_match`` paramater
    in the ``openstack_logstreamer_input`` section in the ``heka-openstack.toml.j2``
    template file in ``ansible/roles/comm/templates`` to deliver log messages to
    Elasticsearch.

* Logrotation

  - For OpenStack services there should be a ``cron-logrotate-PROJECT.conf.j2``
    template file in ``ansible/roles/common/templates`` with the following
    content:

    .. code::

       "/var/log/kolla/PROJECT/*.log"
       {
       }

  - For OpenStack services there should be a entry in the ``services`` list
    in the ``cron.json.j2`` template file in ``ansible/roles/common/templates``.

* Documentation

  - For OpenStack services there should be an entry in the list ``OpenStack services``
    in the ``README.rst`` file.

  - For infrastructure services there should be an entry in the list
    ``Infrastructure components`` in the ``README.rst`` file.

* Syntax

  - All YAML data files should start with three dashes (``---``).

Other than the above, most roles follow the following pattern:

  -  ``Register``: Involves registering the service with Keystone, creating endpoints, roles,
    users, etc.

  -  ``Config``: Distributes the config files to the nodes to be pulled into the container on
    startup.

  - ``Bootstrap``: Creating the database (but not tables), database user for the service,
    permissions, etc.

  - ``Bootstrap Service``: Starts a one shot container on the host to create the database tables,
    and other initial run time config.

  - ``Start``: Start the service(s).
