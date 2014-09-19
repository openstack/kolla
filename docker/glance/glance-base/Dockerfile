FROM docker.usersys.redhat.com/lhh1/rhel-osp-base
MAINTAINER Lars Kellogg-Stedman <lars@redhat.com>

RUN yum -y install \
	openstack-utils \
	openstack-glance \
	python-keystoneclient \
	mariadb; yum clean all

RUN mkdir /opt/glance
COPY config-glance.sh /opt/glance/config-glance.sh

