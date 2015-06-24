
# Integrating with Kolla

This guide describes how to integrate with Kolla.  The main integration path is
via docker-compose using docker-compose YML files.  Each container set has
a common YML and associated `openstack.env`.  The `openstack.env` file
describes the command line environment to pass to the docker-compose yml files.

## Why integrate with Kolla?

Integrating with Kolla takes a hard part of managing an OpenStack system,
specifically managing the container images, and places the burden on a third
party project.  We strive to do an excellent job of providing world-class
OpenStack containers at least as a reference architecture, and possibly as what
may be desirable to deploy into live production.

## Docker Command Line Arguments

Every container set YML file includes the necessary docker CLI operations
needed to launch the container in a tidy YML file.  Instead of guessing which
set of command line operations are needed per container, the docker-compose
YML file can be used directly and will pass the appropriate command line
values to the container on container start.

The parameterized docker features used by kolla are:

* --pid=host
* --net=host
* -v host:container
* --privileged

These parameterized features are not exposed to the user.  Instead they are
executed via docker-compose.

## Environment Variables

Rather then document which individual containers require specific configuration
variables, Kolla integration requires passing all configuration variables to
all containers.  This allows a simple method of ensuring every type of node
(controller, storage, compute) receives the same configuration.

### Environment Variable KEY/VALUE pairs

    DEBUG_LOGGING=<true|false> - Defaults to false. Enable/disable debug level logging for all OpenStack services.
    VERBOSE_LOGGING=<true|false> - Defaults to true. Enable/disable verbose level logging for all OpenStack services.
    NOVA_LOG_DIR=<none> - Defaults to none. The base directory used for relative Nova --log-file paths.
    NEUTRON_LOG_DIR<none> - Defaults to none. The base directory used for relative Neutron --log-file paths.
    NOVA_API_LOG_FILE=<none> Defaults to none. Name of Nova API log file to output to. If no default is set, logging will go to stdout.
    NOVA_CONDUCTOR_LOG_FILE=<none> Defaults to none. Name of Nova Conductor log file to output to. If no default is set, logging will go to stdout.
    NOVA_SCHEDULER_LOG_FILE=<none> Defaults to none. Name of Nova Scheduler log file to output to. If no default is set, logging will go to stdout.
    NOVA_COMPUTE_LOG_FILE=<none> Defaults to none. Name of Nova Compute log file to output to. If no default is set, logging will go to stdout.
    NEUTRON_SERVER_LOG_FILE=<none> Defaults to none. Name of Neutron Server log file to output to. If no default is set, logging will go to stdout.
    NEUTRON_L3_AGENT_LOG_FILE=<none> Defaults to none. Name of Neutron L3 Agent log file to output to. If no default is set, logging will go to stdout.
    NEUTRON_LINUXBRIDGE_AGENT_LOG_FILE=<none> Defaults to none. Name of Neutron Linux Bridge Agent log file to output to. If no default is set, logging will go to stdout.
    NEUTRON_METADATA_AGENT_LOG_FILE=<none> Defaults to none. Name of Neutron Metadata Agent log file to output to. If no default is set, logging will go to stdout.
    ADMIN_USER_PASSWORD=<steakfordinner> - The admin user password
    ADMIN_TENANT_NAME=<admin> - tenant name
    FLAT_INTERFACE=<eth1> - nova networking flat interface device name
    DB_CLUSTER_BIND_ADDRESS=<subnet address/IP> - Defaults to 0.0.0.0. Listening address for database.
    DB_CLUSTER_INIT_DB=<true|false> - Defaults to false. Configures if Galera should be initialized.
    DB_CLUSTER_NAME=<cluster-name>. Defaults to kollacluster. Galera cluster name.
    DB_CLUSTER_NODES=<cluster-nodes>. Defaults to none. List of nodes in Galera cluster, separated by comma(IP address or hostname).
    DB_CLUSTER_WSREP_METHOD=<rsync|mysqldump|xtremebackup|xtremebackup-v2> - Defaults to mysqldump. Galera replication method.
    GLANCE_API_SERVICE_HOST=<IP> - address where glance API is running>
    GLANCE_DB_NAME=<glance> - DB name of glance service
    GLANCE_DB_PASSWORD=<password> - <Glance DB password>
    GLANCE_DB_USER=<glance> - User name of glance in the database
    GLANCE_KEYSTONE_PASSWORD=<password> - Keystone DB password
    GLANCE_KEYSTONE_USER=<keystone> - Glance Keystone User
    GLANCE_REGISTRY_SERVICE_HOST=<glance IP> Glance registry service host
    KEYSTONE_ADMIN_PASSWORD=<password>
    KEYSTONE_ADMIN_SERVICE_HOST=<IP> - IP Address of Keystone Host
    KEYSTONE_ADMIN_SERVICE_PORT=<5000> - Port where Keystone operates
    KEYSTONE_ADMIN_TOKEN=<keystone-secret> - A token used to access Keystone
    KEYSTONE_AUTH_PROTOCOL=<http> - The keystone authentication protocol
    KEYSTONE_DB_PASSWORD=<password> - The password used to access Keystone in the DB
    KEYSTONE_PUBLIC_SERVICE_HOST=<IP> - The IP address where Keystone is running
    MARIADB_ROOT_PASSWORD=<mariadb root password> - defines the MariaDB root password
    MARIADB_SERVICE_HOST=<IP> - The IP Address where Mariadb is running
    NETWORK_MANAGER=<nova|neutron> - Use Nova or Neutron networking
    NOVA_API_SERVICE_HOST=<IP> - The IP Address where the Nova API Service is hosted
    METADATA_HOST=<IP> - The IP address of the Nova Metadata service
    ENABLED_APIS=<ec2,osapi_compute,metadata> - Enabled Nova API services.
    NOVA_DB_NAME=<nova> - The name of the nova entry in the database
    NOVA_DB_PASSWORD=<password> - The password used to access nova
    NOVA_DB_USER=<nova> - The name of the nova DB password
    NOVA_EC2_API_SERVICE_HOST=<IP> - The IP Address where the Nova EC2 API is hosted
    arn't these two the same?
    NOVA_EC2_SERVICE_HOST=<IP> _ The IP Address where the Nova EC2 service is hosted
    NOVA_VNCSERVER_PROXYCLIENT_ADDRESS=<IP> The IP address for the VNC Proxy Client to use
    NOVA_VNCSERVER_LISTEN_ADDRESS=<IP> The IP address for the VNC Server to use
    NOVA_NOVNC_BASE_ADDRESS=<IP/DNS Name> The IP/DNS Name to use for the NOVNC Base URL
    NOVA_NOVNC_PROXY_PORT=<6080> The TCP port used by Nova NoVNC
    NOVA_KEYSTONE_PASSWORD=<password> - The Nova keystone password
    NOVA_KEYSTONE_USER=<nova> - The Nova keystone username
    NEUTRON_DB_NAME=<neutron> - The name of the Neutron database
    NEUTRON_DB_USER=<neutron> - The name used by Neutron to access the Neutron database
    NEUTRON_DB_PASSWORD=<password> The password used by Neutron to access the Neutron database
    NEUTRON_KEYSTONE_USER=<neutron> - The name used by Neutron to communicate with Keystone
    NEUTRON_KEYSTONE_PASSWORD=<neutron> - The password used by Neutron to communicate with Keystone
    NEUTRON_SERVER_SERVICE_HOST=<$HOST_IP> - The IP address/hostname used to commuicate with the Neutron API
    NEUTRON_SHARED_SECRET=<sharedsecret> - The shared secret used between Neutron/Nova to secure metadata communication
    NEUTRON_API_PASTE_CONFIG=</usr/share/neutron/api-paste.ini> - Location of Neutron's API paste config file
    TYPE_DRIVERS=<flat,vxlan> - List of network type driver entrypoints to be loaded
    TENANT_NETWORK_TYPES=<flat,vxlan> - List of network_types to allocate as tenant networks
    MECHANISM_DRIVERS=<linuxbridge,l2population> - List of networking mechanism driver entrypoints to be loaded
    NEUTRON_FLAT_NETWORK_NAME=<physnet1> - List of physical_network names with which flat networks can be created
    NEUTRON_FLAT_NETWORK_INTERFACE=<eth1> - List of physical interface names that connect to physical_networks
    HEAT_DB_NAME=<heat> - The heat DB name
    HEAT_DB_PASSWORD=<kolla> - The heat db password
    HEAT_KEYSTONE_PASSWORD=<heat> - The keystone password for the heat user
    HEAT_API_SERVICE_HOST=<IP> - The IP Address where the Heat API service is hosted
    HEAT_API_CFN_SERVICE_HOST=<IP> - The IP Address where Heat users will contact the heat-engine in search for meta data
    HEAT_API_CFN_URL_HOST=<IP> - The IP Address where Heat virtual machines will contact the heat-engine to signal wait conditions
    INIT_CINDER_DB=<true|false> - Initialize or update the Cinder db
    INIT_DESIGNATE_DB=<true|false> - Initialize or update the Designate db
    INIT_GLANCE_DB=<true|false> - Initialize or update the Glance db
    INIT_HEAT_DB=<true|false> - Initialize or update the Heat db
    INIT_KEYSTONE_DB=<true|false> - Initialize or update the Keystone db
    INIT_NOVA_DB=<true|false> - Initialize or update the Nova db
    PUBLIC_INTERFACE=<eth1> - The nova public interface
    PUBLIC_IP=<Host IP Address> - The IP Address of this host
    RABBITMQ_PASS=<rabbit> - The rabbitmq password used to join AMQP
    RABBITMQ_SERVICE_HOST=<IP> - The IP Address where the Rabbit service is running
    RABBITMQ_USER=<rabbit> - The RabbitMQ user name
    RABBIT_PASSWORD=<password> - The RabbitMQ password
    RABBIT_USERID=<rabbit> - The RabbitMQ user id on the host
    MAGNUM_DB_NAME=<magnum> - The Magnum database name
    MAGNUM_DB_PASSWORD=<kolla> - The Magnum database password
    MAGNUM_KEYSTONE_PASSWORD=<magnum> - The Magnum keystone password
    MAGNUM_API_SERVICE_HOST=<IP> - The Magnum Host IP address
    MAGNUM_API_SERVICE_PORT=<9511> - The Magnum port
    DESIGNATE_DB_NAME=<designate> - The Designate database name
    DESIGNATE_DB_PASSWORD=<designatedns> - The Designate database password
    DESIGNATE_KEYSTONE_PASSWORD=<designate> - The keystone password for the designate user
    DESIGNATE_BIND9_RNDC_KEY=<KEY> - The rndc/bind key to use for communication between pool_manager and bind9
    DESIGNATE_MASTERNS=<IP> - The IP Address of the master (primary) DNS server (the backend)
    DESIGNATE_BACKEND=<bind9> - The backend to use in Designate, currently only bind9 is supported
    DESIGNATE_SLAVENS=<IP> - The IP Address of a slave nameserver under control of pool_manager
    DESIGNATE_API_SERVICE_HOST=<IP> - The IP Address of the Designate API
    DESIGNATE_API_SERVICE_PORT=<9001> - The port of the Designate API
    DESIGNATE_MDNS_PORT=<5354> - The port of the Designate MiniDNS server acting as master server
    DESIGNATE_DNS_PORT=<53> - The port of the Designate-backed DNS slaves that are used by the world
    DESIGNATE_ALLOW_RECURSION=<true|false> - Configure a recursive nameserver
    DESIGNATE_DEFAULT_POOL_NS_RECORD=<ns1.example.org.> - Name of server used to generate NS records
    DESIGNATE_SINK_NOVA_DOMAIN_NAME=<nova.example.org.> - Name of domain used to create records from Nova notifications
    DESIGNATE_SINK_NEUTRON_DOMAIN_NAME=<neutron.example.org.> - Name of domain used to create records from Neutron notifications
    DESIGNATE_SINK_NOVA_FORMATS=<("%(octet0)s-%(octet1)s-%(octet2)s-%(octet3)s.%(domain)s" "%(hostname)s.%(domain)s")> - List of formats for records that will be created by Nova handler
    DESIGNATE_SINK_NEUTRON_FORMATS=<("%(octet0)s-%(octet1)s-%(octet2)s-%(octet3)s.%(domain)s" "%(hostname)s.%(domain)s")> - List of formats for records that will be created by Neutron handler
    CINDER_API_SERVICE_HOST=<IP> - The IP Address where the Cinder service is running
    CINDER_API_SERVICE_PORT=<8776> - Port where Cinder operates
    CINDER_API_SERVICE_LISTEN=<IP> - The IP Address where the Cinder API listens
    CINDER_KEYSTONE_USER=<cinder> - Cinder Keystone User
    CINDER_KEYSTONE_PASSWORD=<password> - The Cinder Keystone password
    CINDER_ADMIN_PASSWORD=<password> - The Cinder password
    CINDER_DB_NAME=<cinder> - Cinder's DB name
    CINDER_DB_USER=<cinder> - User name of Cinder in the database
    CINDER_DB_PASSWORD=<password> - Cinder DB password
    CINDER_BACKUP_DRIVER=<driver> - The backup driver for Cinder
    CINDER_BACKUP_MANAGER=<manager> - The backup manager for Cinder
    CINDER_BACKUP_API_CLASS=<api> - The cinder-backup api class
    CINDER_BACKUP_NAME_TEMPLATE=<template> - The naming template for Cinder backups
    ISCSI_HELPER=<lioadm> - The ISCSI user tool to use
    ISCSI_IP_ADDRESS=<IP> - The IP Address to connect to ISCSI
    CINDER_LVM_LO_VOLUME_SIZE=<size> - The size of the volume group (4G)
    CINDER_VOLUME_GROUP=<cinder-volumes> - The name of the volume group
    CINDER_VOLUME_BACKEND_NAME=<LVM_iSCSI57> - The backend name for a given driver implementation
    CINDER_VOLUME_DRIVER=<cinder.volume.drivers.lvm.LVMISCSIDriver> - The driver used for volume creation
    CINDER_ENABLED_BACKEND=<lvm57> - A list of backend names to use
    INIT_CINDER_DB=<true|false> - Initialize or update the cinder db
    KEEPALIVED_HOST_PRIORITIES=<host1:100,host2:99> - Map of priorities per node. Priorities have to be unique.

[Minimum environment variable setup guide.](https://github.com/stackforge/kolla/blob/master/docs/minimal-environment-vars.md)

## Launching a container set

Pick out a simple container set and launch it as follows:

    $ docker-compose -f compose/rabbitmq.yml up -d

The third party deployment engine should launch the appropriate containers for
the appropriate nodes.  Note the `rabbitmq.yml` used in the example above
expects an `openstack.env` file present in the current working directory.  This
file will be passed as environment data to the container and configure the
container appropriately.


# Conclusion

Integrating with Kolla is as sample as creating an `openstack.env` file, having
a deployment tool write the `openstack.env` file and .yml files to the nodes are
targeted for deployment, and running docker-compose as described in the above
documentation.
