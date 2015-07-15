FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install packages
# TODO check if hostname pkg is needed.
RUN yum -y install mariadb \
    mariadb-server \
    MySQL-python \
    hostname \
    && yum clean all

# Add mysql configuration scripts
COPY config-mysql.sh /opt/kolla/config-mysql.sh
COPY mysql-entrypoint.sh /opt/kolla/mysql-entrypoint.sh

# start mysql
ENTRYPOINT ["/opt/kolla/mysql-entrypoint.sh"]
CMD ["mysqld_safe"]
