FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN echo "[mariadb]" > /etc/yum.repos.d/MariaDB.repo && \
   echo "name = MariaDB" >> /etc/yum.repos.d/MariaDB.repo && \
   echo "baseurl = http://yum.mariadb.org/10.0/centos7-amd64" >> /etc/yum.repos.d/MariaDB.repo && \
   echo "gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB" >> /etc/yum.repos.d/MariaDB.repo && \
   echo "gpgcheck=1" >> /etc/yum.repos.d/MariaDB.repo && \
   yum install -y \
      http://www.percona.com/redir/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm && \
   sed -i 's|$releasever|centos/latest|g' /etc/yum.repos.d/percona-release.repo && \
   yum install -y \
      MariaDB-Galera-server \
      MariaDB-client \
      rsync \
      galera \
      socat \
      hostname \
      percona-xtrabackup \
      pv \
      tar \
      expect

COPY config-galera.sh /opt/kolla/config-galera.sh
COPY start.sh /start.sh

CMD ["/start.sh"]
