.. _multinode:

=============================
Multinode Deployment of Kolla
=============================

Deploy a registry (required for multinode)
==========================================

A Docker registry is a locally hosted registry that replaces the need to pull
from the Docker Hub to get images. Kolla can function with or without a local
registry, however for a multinode deployment a registry is required.

The Docker registry prior to version 2.3 has extremely bad performance because
all container data is pushed for every image rather than taking advantage of
Docker layering to optimize push operations. For more information reference
`pokey registry <https://github.com/docker/docker/issues/14018>`__.


The Kolla community recommends using registry 2.3 or later. To deploy registry
2.3 do the following:

::

    docker run -d -p 4000:5000 --restart=always --name registry registry:2

Note: Kolla looks for the Docker registry to use port 4000. (Docker default is
port 5000)

After starting the registry, it is necessary to instruct Docker that it will
be communicating with an insecure registry. To enable insecure registry
communication on CentOS, modify the ``/etc/sysconfig/docker`` file to contain
the following where 192.168.1.100 is the IP address of the machine where the
registry is currently running:

::

    # CentOS
    other_args="--insecure-registry 192.168.1.100:4000"

For Ubuntu, edit ``/etc/default/docker`` and add:

::

    # Ubuntu
    DOCKER_OPTS="--insecure-registry 192.168.1.100:4000"

Docker Inc's packaged version of docker-engine for CentOS is defective and does
not read the other_args configuration options from ``/etc/sysconfig/docker``.
To rectify this problem, ensure the following lines appear in the drop-in unit
file at ``/etc/systemd/system/docker.service.d/kolla.conf``:

::

    # CentOS
    [Service]
    EnvironmentFile=/etc/sysconfig/docker
    # It's necessary to clear ExecStart before attempting to override it
    # or systemd will complain that it is defined more than once.
    ExecStart=/usr/bin/docker daemon -H fd:// $other_args

And restart docker by executing the following commands:

::

    # CentOS
    systemctl daemon-reload
    systemctl stop docker
    systemctl start docker

    # Ubuntu
    sudo service docker restart

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
