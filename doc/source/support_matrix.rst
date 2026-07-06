.. _support_matrix:

===========================
Kolla Images Support Matrix
===========================

This page describes the supported base container image distributions and
versions, and the Kolla images supported on each of those.

.. _support-matrix-base-images:

Supported base images
=====================

The following base container images are supported:

================== =============================== ================
Distribution       Default base                    Default base tag
================== =============================== ================
Centos             quay.io/centos/centos           stream10
Debian Trixie      debian                          trixie
Rocky Linux        quay.io/rockylinux/rockylinux   10
Ubuntu Noble       ubuntu                          24.04
================== =============================== ================

The remainder of this document outlines which images are supported on which of
these distribution.

Ceph versions in Kolla images
=============================

.. csv-table:: Ceph versions
   :header-rows: 2
   :stub-columns: 1
   :file: ./ceph_versions.csv

Open vSwitch versions in Kolla images
=====================================

.. csv-table:: Open vSwitch versions
   :header-rows: 2
   :stub-columns: 1
   :file: ./openvswitch_versions.csv

OVN versions in Kolla images
============================

.. csv-table:: OVN versions
   :header-rows: 2
   :stub-columns: 1
   :file: ./ovn_versions.csv

Support clause definitions
==========================

T - Tested
----------

Coverage:

* CI in ``kolla-ansible`` is testing that images are functional
* kolla core team is maintaining versions

U - Untested
------------

Coverage:

* CI in ``kolla-ansible`` is *NOT* testing that images are functional
* Many untested services are working fine, but the kolla core team cannot
  guarantee that they are all functional

N - Not Available/Unknown
-------------------------

Not available *(e.g. not buildable)*.
Please see :ref:`unbuildable-images-list`

Deprecations
============

None

x86_64 images
=============

.. csv-table:: x86_64 images
   :header-rows: 1
   :stub-columns: 1
   :widths: auto
   :file: ./matrix_x86.csv

aarch64 images
==============

.. csv-table:: aarch64 images
   :header-rows: 1
   :stub-columns: 1
   :widths: auto
   :file: ./matrix_aarch64.csv

.. _unbuildable-images-list:

Currently unbuildable images
============================

For a list of currently unbuildable images please look into
``kolla/image/unbuildable.py`` file - ``UNBUILDABLE_IMAGES`` dictionary.

SPICE limitations
=================

The OpenStack Compute console type ``spice-direct`` requires that
SPICE support be compiled into the qemu running the instance. Red Hat
removed SPICE support from qemu in RHEL9 onwards, and Rocky Linux has
followed suit, so the stock Rocky Linux container images do not support
``spice-direct`` out of the box.

As a solution, Kolla builds two copies of the ``nova-libvirt`` container
regardless of container distribution. These containers are identical on
other distributions, but for Rocky Linux the community-maintained
`ligenix/enterprise-qemu-spice
<https://copr.fedorainfracloud.org/coprs/ligenix/enterprise-qemu-spice/>`__
COPR repository is installed as it provides a rebuilt ``qemu-kvm``
with SPICE re-enabled for EPEL 9 and EPEL 10. Because this COPR is a
third-party rebuild without a vendor support contract, it is recommended
only for proof-of-concept deployments.

Which container to use for ``nova-libvirt`` is then determined at
``kolla-ansible deploy`` time based on the value of the ``enable_kerbside``
flag.
