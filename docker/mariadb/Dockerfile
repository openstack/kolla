FROM rhel7
MAINTAINER Lars Kellogg-Stedman <lars@redhat.com>

RUN yum -y install mariadb-galera-server
ADD /entrypoint.sh /entrypoint.sh

VOLUME /var/lib/mysql
VOLUME /var/log/mysql

ENTRYPOINT ["/entrypoint.sh"]
CMD ["mysqld_safe"]
