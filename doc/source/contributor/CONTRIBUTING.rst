.. _CONTRIBUTING:

=================
How To Contribute
=================

Basics
======

#. Our source code is hosted on `OpenStack Kolla Git
   <https://git.openstack.org/cgit/openstack/kolla/>`_. Bugs should be filed on
   `launchpad <https://bugs.launchpad.net/kolla>`_.

#. Please follow OpenStack `Gerrit Workflow
   <https://docs.openstack.org/infra/manual/developers.html#development-workflow>`__
   to contribute to Kolla.

#. Note the branch you're proposing changes to. ``master`` is the current focus
   of development. Kolla project has a strict policy of only allowing backports
   in ``stable/branch``, unless when not applicable. A bug in a
   ``stable/branch`` will first have to be fixed in ``master``.

#. Please file a `blueprint of kolla <https://blueprints.launchpad.net/kolla>`__
   for any significant code change and a bug
   for any significant bug fix.  See how to reference a bug or a blueprint in
   the `commit message <https://wiki.openstack.org/wiki/GitCommitMessages>`_.
   For simple changes, contributors may optionally add the text "TrivialFix" to
   the commit message footer to indicate to reviewers a bug is not required.

Please use the existing sandbox repository, available at `sandbox
<https://git.openstack.org/cgit/openstack-dev/sandbox>`_,
for learning, understanding and testing the `Gerrit Workflow
<https://docs.openstack.org/infra/manual/developers.html#development-workflow>`_.

Adding a new service
====================

Kolla aims to both containerise and deploy all services within the OpenStack
"big tent". This is a constantly moving target as the ecosystem grows, so these
guidelines aim to help make adding a new service to Kolla a smooth experience.

The image
---------

Kolla follows `Best practices for writing Dockerfiles
<https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/>`__
when designing and implementing services where at all possible.

We use ``jinja2`` templating syntax to help manage the volume and complexity
that comes with maintaining multiple Dockerfiles for multiple different base
operating systems.

Images should be created under the ``docker`` directory. OpenStack services
should inherit from the provided ``openstack-base`` image, while supporting and
infrastructure services (for example, mongodb) should inherit from ``base``.

Services consisting of only one service should be placed in an image named the
same as that service, for example, ``horizon``. Services that consist of
multiple processes generally use a base image and child images, for example,
``glance-base``, ``glance-api``, and ``glance-registry``.

Jinja2 'blocks' are employed throughout the Dockerfile's to help operators
customise various stages of the build (refer to `Dockerfile Customisation
<https://docs.openstack.org/kolla/latest/admin/image-building.html#dockerfile-customisation>`__)

Some of these blocks are free form however, there are a subset that should be
common to every Dockerfile. The overall structure for a multi container service
is as follows:

.. code-block:: console

   FROM {{ namespace }}/{{ image_prefix }}openstack-base:{{ tag }}
   LABEL maintainer="{{ maintainer }}" name="{{ image_name }}" build-date="{{ build_date }}"

   {% block << service >>_header %}{% endblock %}

   {% import "macros.j2" as macros with context %}

   << binary specific steps >>

   << source specific steps >>

   << common steps >>

   {% block << service >>_footer %}{% endblock %}
   {% block footer %}{% endblock %}

.. note::

   The generic footer block ``{% block footer %}{% endblock %}`` should not be
   included in base images (for example, glance-base).
