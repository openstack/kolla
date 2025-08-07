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
Rocky Linux        quay.io/rockylinux/rockylinux   9
Debian Bookworm    debian                          bookworm
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
