OVS-DPDK Source build
=====================

CentOS and Oracle Linux currently do not provide packages
for ovs with dpdk.
The Ubuntu packages do not support UIO based drivers.
To use the uio_pci_generic driver on Ubuntu a source build is required.

Building ovs with dpdk containers from source
---------------------------------------------

- Append the following to ``/etc/kolla/kolla-build.conf`` to select the version
  of ovs and dpdk to use for your source build.

kolla-build.conf
________________

In this place the ``contrib/template-override/ovs-dpdk.j2`` file:

.. code-block:: console

   [openvswitch-base-plugin-ovs]
   type = git
   location = https://github.com/openvswitch/ovs.git
   reference = v2.7.0

   [openvswitch-base-plugin-dpdk]
   type = git
   location = http://dpdk.org/git/dpdk
   reference = v17.02

.. end

To build the container execute the follow command:

.. code-block:: console

   tools/build.py --template-override \
   contrib/template-override/ovs-dpdk.j2 dpdk

.. end
