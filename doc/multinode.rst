.. _multinode:

=============================
Multinode Deployment of Kolla
=============================

.. _deploy_a_registry:

Deploy a registry (required for multinode)
==========================================

A Docker registry is a locally hosted registry that replaces the need to pull
from the Docker Hub to get images. A local registry is required for a multinode
Kolla deployment.

The Kolla community recommends using registry 2.3 or later. To deploy registry
with version greater than 2.3, do the following:

::

    tools/start-registry

After starting the registry, it is necessary to instruct Docker that it will
be communicating with an insecure registry. To enable insecure registry
communication on CentOS, modify the ``/etc/sysconfig/docker`` file to contain
the following where 192.168.1.100 is the IP address of the machine where the
registry is currently running:

::

    # CentOS
    INSECURE_REGISTRY="--insecure-registry 192.168.1.100:5000"

For Ubuntu, check whether its using upstart or systemd.

::

    # stat /proc/1/exe
    File: '/proc/1/exe' -> '/lib/systemd/systemd'

Edit ``/etc/default/docker`` and add:

::

    # Ubuntu
    DOCKER_OPTS="--insecure-registry 192.168.1.100:5000"

If Ubuntu is using systemd, additional settings needs to be configured.
Copy Docker's systemd unit file to ``/etc/systemd/system/`` directory:

::

    cp /lib/systemd/system/docker.service /etc/systemd/system/docker.service

Next, modify ``/etc/systemd/system/docker.service``, add ``environmentFile``
variable and add ``$DOCKER_OPTS`` to the end of ExecStart in ``[Service]``
section:

::

    # CentOS
    [Service]
    MountFlags=shared
    EnvironmentFile=/etc/sysconfig/docker
    ExecStart=/usr/bin/docker daemon $INSECURE_REGISTRY

    # Ubuntu
    [Service]
    MountFlags=shared
    EnvironmentFile=-/etc/default/docker
    ExecStart=/usr/bin/docker daemon -H fd:// $DOCKER_OPTS

Restart Docker by executing the following commands:

::

    # CentOS or Ubuntu with systemd
    systemctl daemon-reload
    systemctl restart docker

    # Ubuntu with upstart or sysvinit
    sudo service docker restart

.. _edit-inventory:

Edit the Inventory File
=======================

The ansible inventory file contains all the information needed to determine
what services will land on which hosts. Edit the inventory file in the kolla
directory ``ansible/inventory/multinode`` or if kolla was installed with pip,
it can be found in ``/usr/share/kolla``.

Add the ip addresses or hostnames to a group and the services associated with
that group will land on that host:

::

   # These initial groups are the only groups required to be modified. The
   # additional groups are for more control of the environment.
   [control]
   # These hostname must be resolvable from your deployment host
   control01
   192.168.122.24


For more advanced roles, the operator can edit which services will be
associated in with each group. Keep in mind that some services have to be
grouped together and changing these around can break your deployment:

::

   [kibana:children]
   control

   [elasticsearch:children]
   control

   [haproxy:children]
   network

Deploying Kolla
===============

First, check that the deployment targets are in a state where Kolla may deploy
to them:

::

    kolla-ansible prechecks -i <path/to/multinode/inventory/file>

For additional environment setup see the :ref:`deploying-kolla`.

Run the deployment:

::

    kolla-ansible deploy -i <path/to/multinode/inventory/file>
