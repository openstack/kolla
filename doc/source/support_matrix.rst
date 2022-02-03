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

.. note::

   CentOS 7 is no longer supported as a base container image. The Train release
   supports both CentOS 7 and 8 images, and provides a route for migration.

.. note::

   CentOS 8 is no longer supported since it has been marked as End of Life
   and repositories have been removed from CentOS mirrors.

=============== ============ =============================== ================
Distribution    Default base Default base image              Default base tag
=============== ============ =============================== ================
CentOS 8 Stream centos       quay.io/centos/centos           stream8
Debian Buster   debian       debian                          10
RHEL 8          rhel         rhel                            8
Ubuntu Focal    ubuntu       ubuntu                          20.04
=============== ============ =============================== ================

The remainder of this document outlines which images are supported on which of
these distribution.

Support clause definitions
==========================

T - Tested
----------

Coverage:

* CI in ``kolla-ansible`` is testing that images are functional
* kolla core team is maintaining versions

M - Maintained
--------------

Coverage:

* kolla core team is maintaining versions

C - Community maintained
------------------------

Coverage:

* supported by the broader community (not core team) or not supported at all

N - Not Available/Unknown
-------------------------

Not available *(e.g. not buildable)*.
Please see :ref:`unbuildable-images-list`

x86_64 images
=============

.. csv-table:: x86_64 images
   :header-rows: 2
   :stub-columns: 1
   :file: ./matrix_x86.csv

aarch64 images
==============

.. csv-table:: aarch64 images
   :header-rows: 2
   :stub-columns: 1
   :file: ./matrix_aarch64.csv

ppc64le images
==============

.. note:: TODO

.. _unbuildable-images-list:

Currently unbuildable images
============================

For a list of currently unbuildable images please look into
``kolla/image/build.py`` file - ``UNBUILDABLE_IMAGES`` dictionary.

Ceph versions in Kolla images
=============================

.. csv-table:: Ceph versions
   :file: ./ceph_versions.csv

