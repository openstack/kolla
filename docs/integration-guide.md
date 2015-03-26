
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
    HEAT_DB_NAME=<heat> - The heat DB name
    HEAT_DB_PASSWORD=<kolla> - The heat db password
    HEAT_KEYSTONE_PASSWORD=<heat> - The keystone password for the heat user
    HEAT_API_SERVICE_HOST=<IP> - The IP Address where the Heat API service is hosted
    HEAT_API_CFN_SERVICE_HOST=<IP> - The IP Address where Heat will contact the heat-engine in search for meta data
    PUBLIC_INTERFACE=<eth1> - The nova public interface
    PUBLIC_IP=<Host IP Address> - The IP Address of this host
    RABBITMQ_PASS=<rabbit> - The rabbitmq password used to join AMQP
    RABBITMQ_SERVICE_HOST=<IP> - The IP Address where the Rabbit service is running
    RABBITMQ_USER=<rabbit> - The RabbitMQ user name
    RABBIT_PASSWORD=<password> - The RabbitMQ password
    RABBIT_USERID=<rabbit> - The RabbitMQ user id on the host

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
