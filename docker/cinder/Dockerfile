FROM fedora-rdo-base
MAINTAINER rhallise@redhat.com

# Install required packages
RUN yum install -y wget procps-ng net-tools && yum clean all
RUN yum install -y openstack-cinder rabbitmq-server openstack-utils openstack-selinux mariadb-galera-server socat && yum clean all


# Start Cinder
RUN /usr/bin/cinder-api --config-file /usr/share/cinder/cinder-dist.conf --config-file /etc/cinder/cinder.conf --logfile /var/log/cinder/api.log

RUN /usr/bin/cinder-scheduler --config-file /usr/share/cinder/cinder-dist.conf --config-file/etc/cinder/cinder.conf --logfile /var/log/cinder/scheduler.log

RUN /usr/bin/cinder-volume --config-file /usr/share/cinder/cinder-dist.conf --config-file /etc/cinder/cinder.conf --logfile /var/log/cinder/volume.log

ADD ./start /usr/bin/run

CMD ["/usr/bin/run"]
