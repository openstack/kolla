FROM kollaglue/fedora-rdo-base
MAINTAINER Lars Kellogg-Stedman <lars@redhat.com>

RUN yum -y install mariadb-galera-server
ADD /entrypoint.sh /entrypoint.sh

VOLUME /var/lib/mysql
VOLUME /var/log/mariadb

EXPOSE 3306

ENTRYPOINT ["/entrypoint.sh"]
CMD ["mysqld_safe"]
