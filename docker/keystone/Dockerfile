FROM rhel7
MAINTAINER jlabocki@redhat.com

#Install required packages
RUN yum install -y openstack-keystone \
	openstack-utils \
	openstack-selinux \
	mariadb \
	&& yum clean all

ADD ./start.sh /start.sh

CMD ["/start.sh"]
