
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

    ADMIN_TENANT_NAME=<admin> - tenant name
    DB_ROOT_PASSWORD=<mysql root password> - defines the MYSQL root password
    FLAT_INTERFACE=<nova or neutron networking flat interface device name>
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
    MARIADB_SERVICE_HOST=<IP> - The IP Address where mariadb is running
    MYSQL_ROOT_PASSWORD=<password> - The MYSQL password
    NETWORK_MANAGER=<nova|neutron> - Use Nova or Neutron networking
    NOVA_API_SERVICE_HOST=<IP> - The IP Address where the Nova API Service is hosted
    NOVA_DB_NAME=<nova> - The name of the nova entry in the database
    NOVA_DB_PASSWORD=<password> - The password used to access nova
    NOVA_DB_USER=<nova> - The name of the nova DB password
    NOVA_EC2_API_SERVICE_HOST=<IP> - The IP Address where the Nova EC2 API is hosted
    arn't these two the same?
    NOVA_EC2_SERVICE_HOST=<IP> _ The IP Address wher ethe Nova EC2 service is hosted
    NOVA_KEYSTONE_PASSWORD=<password> - The Nova keystone password
    NOVA_KEYSTONE_USER=<nova> - The Nova keystone username
    HEAT_DB_NAME=<heat> - The heat DB name
    HEAT_DB_PASSWORD=<kolla> - The heat db password
    HEAT_KEYSTONE_PASSWORD=<heat> - The keystone password for the heat user
    HEAT_API_SERVICE_HOST=<IP> - The IP Address where the Heat API service is hosted
    PUBLIC_INTERFACE=<eth1> - The nova public interface
    PUBLIC_IP=<Host IP Address> - The IP Address of this host
    RABBITMQ_PASS=<rabbit> - The rabbitmq password used to join AMQP
    RABBITMQ_SERVICE_HOST=<IP> - The IP Address where the Rabbit service is running
    RABBITMQ_USER=<rabbit> - The RabbitMQ user name
    RABBIT_PASSWORD=<password> - The RabbitMQ password
    RABBIT_USERID=<rabbit> - The RabbitMQ user id on the host


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
