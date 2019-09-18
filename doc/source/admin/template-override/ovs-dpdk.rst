OVS-DPDK Source build
=====================

CentOS currently does not provide packages for ovs with dpdk.
The Ubuntu packages do not support UIO based drivers.
To use the uio_pci_generic driver on Ubuntu a source build is required.

Building ovs with dpdk containers from source
---------------------------------------------

Append the following to ``/etc/kolla/kolla-build.conf`` to select the version
of ovs and dpdk to use for your source build.

.. code-block:: console

   [openvswitch-base-plugin-ovs]
   type = git
   location = https://github.com/openvswitch/ovs.git
   reference = v2.10.0

   [openvswitch-base-plugin-dpdk]
   type = git
   location = http://dpdk.org/git/dpdk
   reference = v17.11


To build the container, run the following command inside a cloned kolla
repository:

.. code-block:: console

   tools/build.py -t source --template-override contrib/template-override/ovs-dpdk.j2 ovsdpdk

