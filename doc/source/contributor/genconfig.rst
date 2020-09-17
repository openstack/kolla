===========================
Generating kolla-build.conf
===========================

Install tox and generate the build configuration. The build configuration is
designed to hold advanced customizations when building images.

If you have already cloned the Kolla Git repository to the ``kolla`` folder,
generate the ``kolla-build.conf`` file using the following steps.

.. code-block:: console

   python3 -m pip install tox
   cd kolla/
   tox -e genconfig

The location of the generated configuration file is
``etc/kolla/kolla-build.conf``.
