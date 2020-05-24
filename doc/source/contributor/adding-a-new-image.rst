==================
Adding a new image
==================

Kolla follows `Best practices for writing Dockerfiles
<https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/>`__
where at all possible.

We use ``jinja2`` templating syntax to help manage the volume and complexity
that comes with maintaining multiple Dockerfiles for multiple different base
operating systems.

Dockerfiles should be placed under the ``docker`` directory. OpenStack services
should inherit from the provided ``openstack-base`` image, and
infrastructure services (for example: ``fluentd``) should inherit from
``base``.

Projects consisting of only one service should be placed in an image named the
same as that service, for example: ``horizon``. Services that consist of
multiple processes generally use a base image and child images, for example:
``cinder-base``, ``cinder-api``, ``cinder-scheduler``, ``cinder-volume``,
``cinder-backup``.

Jinja2 `blocks` are employed throughout the Dockerfiles to help operators
customise various stages of the build (refer to :ref:`Dockerfile Customisation
<dockerfile-customisation>`)

Some of these blocks are free form. However, there is a subset that should be
common to every Dockerfile. The overall structure of a Dockerfiles of an
OpenStack project base image is as follows:

.. code-block:: console

   FROM {{ namespace }}/{{ image_prefix }}openstack-base:{{ tag }}
   {% block labels %}
   LABEL maintainer="{{ maintainer }}" name="{{ image_name }}" build-date="{{ build_date }}"
   {% endblock %}

   {% block << service >>_header %}{% endblock %}

   {% import "macros.j2" as macros with context %}

   << binary specific steps >>

   << source specific steps >>

   << common steps >>

   {% block << service >>_footer %}{% endblock %}
   {% block footer %}{% endblock %}

.. note::

   The generic footer block ``{% block footer %}{% endblock %}`` should **not** be
   included in base images (for example: ``cinder-base``).

It's probably easiest to identify the most similar service being already
provided, copy its Dockerfile structure and amend it to new needs.
