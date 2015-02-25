MariaDB Container Set
=====================

The MariaDB database application has been organized into two containers,
known as a [container-set][] within the Kolla project. One container runs
the MariaDB application and the other stores the actual data.

Operational efficiencies and service stability is provided by
separating the application from the stored data. For example, stored data
can be backed-up or restored without touching the MariaDB application
component.

The containers work in a cooperative fashion by using [docker-compose][]
(aka Fig) to ensure the containers are co-located on the same host.
With docker-compose, you can manage the containers collectively
as a single unit.

Here is a sample docker-compose yaml file for using both MariaDB containers:

```
mariadbdata:
  image: kollaglue/centos-rdo-mariadb-data
  volumes:
    - /var/lib/mysql:/var/lib/mysql
    - /var/log/mariadb:/var/log/mariadb
  net: "host"
  privileged: true
mariadbapp:
  image: kollaglue/centos-rdo-mariadb-app
  env_file:
    - openstack.env
  volumes_from:
    - mariadbdata
  net: "host"
  ports:
    - "3306:3306"
  privileged: true
```

In addition to the MariaDB application being organized across two containers, the data
container follows the [data-only container][] design pattern. In this design pattern,
a dedicated container is used to perform a host mount and separate application
container(s) mount volumes from the data-only container instead of performing the host
mount directly. In the example above, the MariaDbApp container mounts the /var/lib/mysql
and /var/log/mariadb volumes through the MariaDbData container instead of mounting
these directly to the Docker host.

[docker-compose]: http://www.fig.sh/
[container-set]: https://review.openstack.org/#/c/153798/
[data-only container]: http://www.tech-d.net/2013/12/16/persistent-volumes-with-docker-container-as-volume-pattern/
