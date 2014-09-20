FROM fedora-rdo-base
MAINTAINER jlabocki@redhat.com

#Install required packages
RUN yum install -y openstack-keystone \
	openstack-utils \
	mariadb \
	&& yum clean all

ADD ./start.sh /start.sh

CMD ["/start.sh"]
