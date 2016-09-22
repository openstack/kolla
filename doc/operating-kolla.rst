.. _operating-kolla:

===============
Operating Kolla
===============

Upgrading
=========
Kolla's strategy for upgrades is to never make a mess and to follow consistent
patterns during deployment such that upgrades from one environment to the next
are simple to automate.

Kolla implements a one command operation for upgrading an existing deployment
consisting of a set of containers and configuration data to a new deployment.

Kolla uses the ``x.y.z`` semver nomenclature for naming versions. Kolla's
Liberty version is ``1.0.0`` and the Mitaka version is ``2.0.0``. The Kolla
community commits to release z-stream updates every 45 days that resolve
defects in the stable version in use and publish those images to the Docker Hub
registry. To prevent confusion, the Kolla community recommends using an alpha
identifier ``x.y.z.a`` where ``a`` represents any customization done on the
part of the operator. For example, if an operator intends to modify one of the
Docker files or the repos from the originals and build custom images for the
Liberty version, the operator should start with version 1.0.0.0 and increase
alpha for each release. Alpha tag usage is at discretion of the operator. The
alpha identifier could be a number as recommended or a string of the operator's
choosing.

If the alpha identifier is not used, Kolla will deploy or upgrade using the
version number information contained in the release. To customize the
version number uncomment openstack_version in globals.yml and specify
the version number desired.

For example, to deploy a custom built Liberty version built with the
``kolla-build --tag 1.0.0.0`` operation, change globals.yml::

    openstack_version: 1.0.0.0

Then run the command to deploy::

    kolla-ansible deploy

If using Liberty and a custom alpha number of 0, and upgrading to 1, change
globals.yml::

    openstack_version: 1.0.0.1

Then run the command to upgrade::

    kolla-ansible upgrade

.. note:: Varying degrees of success have been reported with upgrading
  the libvirt container with a running virtual machine in it. The libvirt
  upgrade still needs a bit more validation, but the Kolla community feels
  confident this mechanism can be used with the correct Docker graph driver.

.. note:: The Kolla community recommends the btrfs or aufs graph drivers for
  storing data as sometimes the LVM graph driver loses track of its reference
  counting and results in an unremovable container.

.. note:: Because of system technical limitations, upgrade of a libvirt
  container when using software emulation (``virt_driver=qemu`` in nova.conf),
  does not work at all. This is acceptable because KVM is the recommended
  virtualization driver to use with Nova.


Tips and Tricks
===============
Kolla ships with several utilities intended to facilitate ease of operation.

``tools/cleanup-containers`` can be used to remove deployed containers from the
system. This can be useful when you want to do a new clean deployment. It will
preserve the registry and the locally built images in the registry, but will
remove all running Kolla containers from the local Docker daemon. It also
removes the named volumes.

``tools/cleanup-host`` can be used to remove remnants of network changes
triggered on the Docker host when the neutron-agents containers are launched.
This can be useful when you want to do a new clean deployment, particularly one
changing the network topology.

``tools/cleanup-images`` can be used to remove all Docker images built by Kolla
from the local Docker cache.
