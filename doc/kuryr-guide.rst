Kuryr in Kolla
==============

"Kuryr is a Docker network plugin that uses Neutron to provide networking
services to Docker containers. It provides containerized images for the common
Neutron plugins" [1]. Kuryr requires at least Keystone and neutron. Kolla makes
kuryr deployment faster and accessible.

Requirements
------------

* A minimum of 3 hosts for a vanilla deploy

Preparation and Deployment
--------------------------

To allow docker daemon connect to the etcd, add the following in the docker.server
file.

::

  ExecStart= -H tcp://172.16.1.13:2375 -H unix:///var/run/docker.sock --cluster-store=etcd://172.16.1.13:2379 --cluster-advertise=172.16.1.13:2375

The IP address is host runnning the etcd service. ```2375``` is port that allows
Docker daemon to be accessed remotely. ```2379``` is the etcd listening port.


By default etcd and kuryr are disabled in the ``group_vars/all.yml``. In order to
enable them, you need to edit the file globals.yml and set the following
variables

::

  enable_etcd: "yes"
  enable_kuryr: "yes"

Deploy the OpenStack cloud and kuryr network plugin

::

  kolla-ansible deploy

Create a Virtual Network
--------------------------------

::

    docker network create -d kuryr --ipam-driver=kuryr --subnet=10.1.0.0/24 --gateway=10.1.0.1 docker-net1

To list the created network:

::

    docker network ls

The created network is also available from openstack CLI:

::

    openstack network list


[1] https://github.com/openstack/kuryr
