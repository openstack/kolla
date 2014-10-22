FROM kollaglue/fedora-rdo-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install mariadb-galera-server; yum clean all
ADD /entrypoint.sh /entrypoint.sh

VOLUME /var/lib/mysql
VOLUME /var/log/mariadb

EXPOSE 3306

ENTRYPOINT ["/entrypoint.sh"]
CMD ["mysqld_safe"]
