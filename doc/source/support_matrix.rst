.. _support_matrix:

===========================
Kolla Images Support Matrix
===========================

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
