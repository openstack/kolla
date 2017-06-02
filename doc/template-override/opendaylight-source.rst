==================
OpenDaylight Build
==================

To build OpenDaylight, use of a template override
`opendaylight-template-overrides.j2` is needed.
The template override enables OpenDaylight use
with OpenStack by installing required networking-odl
plugin in neutron-server container.

If you wish to install a different version of OpenDaylight
then distro packages, use a source build (in most cases this is
a prebuilt binary package).

Building OpenDaylight Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- For source builds append the following to kolla-build.conf,
  selecting the version of OpenDaylight to use for your source build.

- Change `opendaylight_distro` to match the folder where OpenDaylight
  build resides. For example, if using prebuilt archive from OpenDaylight
  downloads `distribution-karaf-0.6.0-Carbon.tar.gz` becomes
  `distribution-karaf-0.6.0-Carbon`.

kolla-build.conf
________________
.. code-block:: console

    opendaylight_distro = distribution-karaf-0.6.0-Carbon
    [opendaylight]
    type = url
    location = https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/distribution-karaf/0.6.0-Carbon/distribution-karaf-0.6.0-Carbon.tar.gz

Build the container (source or binary) by executing the following command:

::

    kolla-build --template-override contrib/template-override/opendaylight-template-overrides.j2 opendaylight
