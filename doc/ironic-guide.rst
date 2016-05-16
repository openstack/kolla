.. _ironic-guide:

===============
Ironic in Kolla
===============

Overview
========
Currently Kolla can deploy the Ironic services:

- ironic-api
- ironic-conductor
- ironic-inspector

As well as a required PXE service, deployed as ironic-pxe.

Current status
==============
The Ironic implementation is "tech preview", so currently instances can only be
deployed on baremetal. Further work will be done to allow scheduling for both
virtualized and baremetal deployments.

Post-deployment configuration
=============================
Configuration based off upstream documentation_.

Again, remember that enabling Ironic reconfigures nova compute (driver and
scheduler) as well as changes neutron network settings. Further neutron setup
is required as outlined below.

Create the flat network to launch the instances:
::

    neutron net-create --tenant-id $TENANT_ID sharednet1 --shared \
    --provider:network_type flat --provider:physical_network physnet1

    neutron subnet-create sharednet1 $NETWORK_CIDR --name $SUBNET_NAME \
    --ip-version=4 --gateway=$GATEWAY_IP --allocation-pool \
    start=$START_IP,end=$END_IP --enable-dhcp

And then the above ID is used to set cleaning_network_uuid in the neutron
section of ironic.conf.

.. _documentation: http://docs.openstack.org/developer/ironic/deploy/install-guide.html
