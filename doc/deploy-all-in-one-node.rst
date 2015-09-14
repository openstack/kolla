Deploy OpenStack all in one node using Ansible
==============================================


Deploy OpenStack to ubuntu host(ubuntu docker image)
----------------------------------------------------



The machine minimal requirements:

- two network interfaces.

The machine recommended requirements:

- two network interfaces.
- more than 8gb main memory.
- at least 40gb disk space.

To verify the Ubuntu kernel is sufficient to operate Kolla, run the command:

::

    docker run -i -t --net=host ubuntu su

If the command displays "su: System error",
the system suffers from this DockerBug_. This is a possible way to solve the issue:

::

    sudo apt-get install linux-image-generic-lts-vivid
    sudo reboot



The guide assumes that you have build images using the following command.

::

    tools/build.py -n 172.22.2.81:4000/kollaglue --base ubuntu --type source --push

The IP, "172.22.2.81", is the host running private docker registry.
To deploy a private docker registry,
please read the document  DeployingRegistryServer_.

First, add ``--insecure-registry 172.22.2.81:4000``
to ``DOCKER_OPTS`` in ``/etc/default/docker``.
And restart the docker service.
This will permit Docker to pull from the deployment's private registry.

Clone the kolla repository and copy kolla config to ``"/etc"``:

::

    git clone https://github.com/openstack/kolla
    cd kolla
    cp -rf etc/kolla/ /etc/

And modify the file, ``"/etc/kolla/globals.yml"``. Do the below tasks.

- Set ``"kolla_base_distro"`` to ``"ubuntu"``.
- Set ``"kolla_install_type"`` to ``"source"``.
- Set ``"docker_registry"`` to ``"172.22.2.81:4000"``.
- Change kolla_internal_address value.
  Specify an unisued IP address in the deployment environment

Change the following values if needed:

- network_interface
- neutron_external_interface

After doing these tasks, run the following command in kolla directory:

::

    tools/kolla-ansible -i ansible/inventory/all-in-one -p ansible/site.yml deploy


Deployment takes between 10 and 15 minutes from
a local private registry on gigabit networks.


.. _DeployingRegistryServer: https://docs.docker.com/registry/deploying/
.. _DockerBug: https://github.com/docker/docker/issues/5899
