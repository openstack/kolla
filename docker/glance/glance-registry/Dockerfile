FROM docker.usersys.redhat.com/lhh1/rhel-osp-base
MAINTAINER Lars Kellogg-Stedman <lars@redhat.com>

yum -y install \
	openstack-utils \
	openstack-glance \
	mariadb; yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]

