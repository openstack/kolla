.. troubleshooting:

=====================
Troubleshooting Guide
=====================

Failures
========

If Kolla fails, often it is caused by a CTRL-C during the deployment
process or a problem in the ``globals.yml`` configuration.

To correct the problem where Operators have a misconfigured environment, the
Kolla community has added a precheck feature which ensures the deployment
targets are in a state where Kolla may deploy to them. To run the prechecks,
execute:

Production
==========

::

    kolla-ansible prechecks

Development
===========

::

    ./tools/kolla-ansible prechecks

If a failure during deployment occurs it nearly always occurs during evaluation
of the software. Once the Operator learns the few configuration options
required, it is highly unlikely they will experience a failure in deployment.

Deployment may be run as many times as desired, but if a failure in a
bootstrap task occurs, a further deploy action will not correct the problem.
In this scenario, Kolla's behavior is undefined.

The fastest way during to recover from a deployment failure is to
remove the failed deployment:

Production
==========

::

    kolla-ansible destroy -i <<inventory-file>>

Development
===========

::

    ./tools/kolla-ansible destroy -i <<inventory-file>>

Any time the tags of a release change, it is possible that the container
implementation from older versions won't match the Ansible playbooks in a new
version. If running multinode from a registry, each node's Docker image cache
must be refreshed with the latest images before a new deployment can occur. To
refresh the docker cache from the local Docker registry:

Production
==========

::

    kolla-ansible pull

Development
===========

::

    ./tools/kolla-ansible pull

Debugging Kolla
===============

The status of containers after deployment can be determined on the deployment
targets by executing:

::

    docker ps -a

If any of the containers exited, this indicates a bug in the container. Please
seek help by filing a `launchpad bug`_ or contacting the developers via IRC.

The logs can be examined by executing:

::

    docker exec -it heka bash

The logs from all services in all containers may be read from
``/var/log/kolla/SERVICE_NAME``

If the stdout logs are needed, please run:

::

    docker logs <container-name>

Note that most of the containers don't log to stdout so the above command will
provide no information.

To learn more about Docker command line operation please refer to `Docker
documentation <https://docs.docker.com/reference/commandline/cli/>`__.

When ``enable_central_logging`` is enabled, to view the logs in a web browser
using Kibana, go to:

::

    http://<kolla_internal_vip_address>:<kibana_server_port>
    or http://<kolla_external_vip_address>:<kibana_server_port>

and authenticate using ``<kibana_user>`` and ``<kibana_password>``.

The values ``<kolla_internal_vip_address>``, ``<kolla_external_vip_address>``
``<kibana_server_port>`` and ``<kibana_user>`` can be found in
``<kolla_install_path>/kolla/ansible/group_vars/all.yml`` or if the default
values are overridden, in ``/etc/kolla/globals.yml``. The value of
``<kibana_password>`` can be found in ``/etc/kolla/passwords.yml``.

.. note:: When you log in to Kibana web interface for the first time, you are
   prompted to create an index. Please create an index using the name ``log-*``.
   This step is necessary until the default Kibana dashboard is implemented in
   Kolla.

.. _launchpad bug: https://bugs.launchpad.net/kolla/+filebug
