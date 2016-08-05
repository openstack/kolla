.. _security:

==============
Kolla Security
==============

Non Root containers
===================
The OpenStack services, with a few exceptions, run as non root inside of
Kolla's containers. Kolla uses the Docker provided USER flag to set the
appropriate user for each service.

SELinux
=======
The state of SELinux in Kolla is a work in progress. The short answer is you
must disable it until selinux polices are written for the Docker containers.

To understand why Kolla needs to set certain selinux policies for services that
you wouldn't expect to need them (rabbitmq, mariadb, glance, etc.) we must take
a step back and talk about Docker.

Docker has not had the concept of persistent containerized data until recently.
This means when a container is run the data it creates is destroyed when the
container goes away, which is obviously no good in the case of upgrades.

It was suggested data containers could solve this issue by only holding data if
they were never recreated, leading to a scary state where you could lose access
to your data if the wrong command was executed. The real answer to this problem
came in Docker 1.9 with the introduction of named volumes. You could now
address volumes directly by name removing the need for so called **data
containers** all together.

Another solution to the persistent data issue is to use a host bind mount which
involves making, for sake of example, host directory ``var/lib/mysql``
available inside the container at ``var/lib/mysql``. This absolutely solves the
problem of persistent data, but it introduces another security issue,
permissions. With this host bind mount solution the data in ``var/lib/mysql``
will be owned by the mysql user in the container. Unfortunately, that mysql
user in the container could have any UID/GID and thats who will own the data
outside the container introducing a potential security risk. Additionally, this
method dirties the host and requires host permissions to the directories to
bind mount.

The solution Kolla chose is named volumes.

Why does this matter in the case of selinux? Kolla does not run the process it
is launching as root in most cases. So glance-api is run as the glance user,
and mariadb is run as the mysql user, and so on. When mounting a named volume
in the location that the persistent data will be stored it will be owned by the
root user and group. The mysql user has no permissions to write to this folder
now. What Kolla does is allow a select few commands to be run with sudo as the
mysql user. This allows the mysql user to chown a specific, explicit directory
and store its data in a named volume without the security risk and other
downsides of host bind mounts. The downside to this is selinux blocks those
sudo commands and it will do so until we make explicit policies to allow those
operations.
