==================
OpenDaylight Build
==================

The `opendaylight-template-overrides.j2` template override shows how to build
an OpenDaylight container image with a different version than the one packaged
with the distro.

Building OpenDaylight Container Images
======================================

kolla-build.conf
----------------

Point to the desired version of OpenDaylight in `kolla-build.conf`:

.. code-block:: ini

   [opendaylight]
   type = url
   location = https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/distribution-karaf/0.6.2-Carbon/distribution-karaf-0.6.2-Carbon.tar.gz

.. end

Build the container by executing the following command:

.. code-block:: console

   kolla-build --type source --template-override contrib/template-override/opendaylight-template-overrides.j2 opendaylight

.. end
