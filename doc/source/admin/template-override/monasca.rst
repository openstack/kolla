==============================================
Building non-standard Monasca container images
==============================================

The `monasca-template-overrides.j2` file shows how to build
any images required for Monasca which are non-standard. Currently this
includes only InfluxDB. When Monasca is upgraded this file will
no longer be required.

InfluxDB
--------

Build the container by executing the following command:

.. code-block:: console

   kolla-build --template-override contrib/template-override/monasca-template-overrides.j2 influxdb

