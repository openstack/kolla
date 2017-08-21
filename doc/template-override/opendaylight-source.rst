==================
OpenDaylight Build
==================

The `opendaylight-template-overrides.j2` template override shows how to build
an OpenDaylight container image with a different version than the one packaged
with the distro.

Building OpenDaylight Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

kolla-build.conf
________________

Point to the desired version of OpenDaylight in `kolla-build.conf`:

.. code-block:: console

    [opendaylight]
    type = url
    location = https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/distribution-karaf/0.6.0-Carbon/distribution-karaf-0.6.0-Carbon.tar.gz

Build the container by executing the following command:

::

    kolla-build --type source --template-override contrib/template-override/opendaylight-template-overrides.j2 opendaylight
