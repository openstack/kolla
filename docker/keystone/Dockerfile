FROM kollaglue/fedora-rdo-base
MAINTAINER Lars Kellogg-Stedman <lars@redhat.com>

#Install required packages
RUN yum -y install dnf dnf-plugins-core; yum clean all
RUN dnf copr enable -y larsks/crux
RUN yum install -y openstack-keystone \
	openstack-utils \
	mariadb \
	crux \
	; yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

EXPOSE 5000 35357

CMD ["/start.sh"]
