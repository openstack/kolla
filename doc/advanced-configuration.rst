.. _advanced-configuration:

======================
Advanced Configuration
======================

Endpoint Network Configuration
==============================

When an OpenStack cloud is deployed, each services' REST API is presented
as a series of endpoints. These endpoints are the admin URL, the internal
URL, and the external URL.

Kolla offers two options for assigning these endpoints to network addresses.
These are combined and separate. For the combined option, all three
endpoints share the same IP address. For the separate option, the external
URL is assigned to an IP address that is different than the IP address
shared by the internal and admin URLs.

The configuration parameters related to these options are:
  - kolla_internal_vip_address
  - network_interface
  - kolla_external_vip_address
  - kolla_external_vip_interface

For the combined option, set the two variables below, while allowing the
other two to accept their default values. In this configuration all REST
API requests, internal and external, will flow over the same network. ::

    kolla_internal_vip_address: "10.10.10.254"
    network_interface: "eth0"

For the separate option, set these four variables. In this configuration
the internal and external REST API requests can flow over separate
networks. ::

    kolla_internal_vip_address: "10.10.10.254"
    network_interface: "eth0"
    kolla_external_vip_address: "10.10.20.254"
    kolla_external_vip_interface: "eth1"

Fully Qualified Domain Name Configuration
=========================================

When addressing a server on the internet, it is more common to use
a name, like www.example.net, instead of an address like 10.10.10.254.
If you prefer to use names to address the endpoints in your kolla
deployment use the variables:

  - kolla_internal_fqdn
  - kolla_external_fqdn

::

    kolla_internal_fqdn: inside.mykolla.example.net
    kolla_external_fqdn: mykolla.example.net

Provisions must be taken outside of kolla for these names to map to the
configured IP addresses. Using a DNS server or the /etc/hosts file are
two ways to create this mapping.

TLS Configuration
=================

An additional endpoint configuration option is to enable or disable
TLS protection for the external VIP. TLS allows a client to authenticate
the OpenStack service endpoint and allows for encryption of the requests
and responses.

.. note:: The kolla_internal_vip_address and kolla_external_vip_address must
   be different to enable TLS on the external network.

The configuration variables that control TLS networking are:

  - kolla_enable_tls_external
  - kolla_external_fqdn_cert

The default for TLS is disabled; to enable TLS networking:

::

    kolla_enable_tls_external: "yes"
    kolla_external_fqdn_cert: "{{ node_config_directory }}/certificates/mycert.pem"


.. note:: TLS authentication is based on certificates that have been
   signed by trusted Certificate Authorities. Examples of commercial
   CAs are Comodo, Symantec, GoDaddy, and GlobalSign. Letsencrypt.org
   is a CA that will provide trusted certificates at no charge. Many
   company's IT departments will provide certificates within that
   company's domain. If using a trusted CA is not possible for your
   situation, you can use OpenSSL to create your own or see the section
   below about kolla generated self-signed certificates.

Two certificate files are required to use TLS securely with authentication.
These two files will be provided by your Certificate Authority. These
two files are the server certificate with private key and the CA certificate
with any intermediate certificates. The server certificate needs to be
installed with the kolla deployment and is configured with the
``kolla_external_fqdn_cert`` parameter. If the server certificate provided
is not already trusted by the client, then the CA certificate file will
need to be distributed to the client.

When using TLS to connect to a public endpoint, an OpenStack client will
have settings similar to this:

::

    export OS_PROJECT_DOMAIN_ID=default
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_NAME=demo
    export OS_USERNAME=demo
    export OS_PASSWORD=demo-password
    export OS_AUTH_URL=https://mykolla.example.net:5000
    # os_cacert is optional for trusted certificates
    export OS_CACERT=/etc/pki/mykolla-cacert.crt
    export OS_IDENTITY_API_VERSION=3

Self-Signed Certificates
========================

.. note:: Self-signed certificates should never be used in production.

It is not always practical to get a certificate signed by a well-known
trust CA, for example a development or internal test kolla deployment. In
these cases it can be useful to have a self-signed certificate to use.

For convenience, the kolla-ansible command will generate the necessary
certificate files based on the information in the ``globals.yml``
configuration file:

 ::

    kolla-ansible certificates

The files haproxy.pem and haproxy-ca.pem will be generated and stored
in the ``/etc/kolla/certificates/`` directory.


OpenStack Service Configuration in Kolla
========================================

.. note:: As of now kolla only supports config overrides for ini based configs.
          An operator can change the location where custom config files are read
          from by editing ``/etc/kolla/globals.yml`` and adding the following
          line.

::

   # The directory to merge custom config files the kolla's config files
   node_custom_config: "/etc/kolla/config"

Kolla allows the operator to override configuration of services. Kolla will
look for a file in ``/etc/kolla/config/<< service name >>/<< config file >>``.
This can be done per-project, per-service or per-service-on-specified-host.
For example to override scheduler_max_attempts in nova scheduler, the operator
needs to create ``/etc/kolla/config/nova/nova-scheduler.conf`` with content:

::

   [DEFAULT]
   scheduler_max_attempts = 100

If the operator wants to configure compute node ram allocation ratio
on host myhost, the operator needs to create file
``/etc/kolla/config/nova/myhost/nova.conf`` with content:

::

   [DEFAULT]
   ram_allocation_ratio = 5.0

The operator can make these changes after services were already deployed by
using following command:

::

    kolla-ansible reconfigure

IP Address Constrained Environments
===================================

If a development environment doesn't have a free IP address available for VIP
configuration, the host's IP address may be used here by disabling HAProxy by
adding:

::

    enable_haproxy: "no"

Note this method is not recommended and generally not tested by the
Kolla community, but included since sometimes a free IP is not available
in a testing environment.

External Elasticsearch/Kibana environment
=========================================

It is possible to use an external Elasticsearch/Kibana environment. To do this
first disable the deployment of the central logging.

::

    enable_central_logging: "no"

Now you can use the parameter ``elasticsearch_address`` to configure the
address of the external Elasticsearch environment.

Non-default <service> port
==========================

It is sometimes required to use a different than default port
for service(s) in Kolla. It is possible with setting <service>_port
in ``globals.yml`` file.
For example:

::

    database_port: 3307

As <service>_port value is saved in different services' configurationso
it's advised to make above change before deploying.

