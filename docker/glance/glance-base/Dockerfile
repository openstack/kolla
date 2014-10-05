FROM kollaglue/fedora-rdo-base
MAINTAINER Dan Radez <dradez@redhat.com>

RUN yum -y install dnf dnf-plugins-core; yum clean all
RUN dnf copr enable -y larsks/crux
RUN yum -y install \
	openstack-utils \
	openstack-glance \
	python-keystoneclient \
	mariadb crux \
	; yum clean all

RUN mkdir /opt/glance
COPY config-glance.sh /opt/glance/config-glance.sh

