FROM kollaglue/fedora-rdo-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

#Install required packages
RUN yum install -y openstack-keystone \
	openstack-utils \
	mariadb \
	; yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

EXPOSE 5000 35357

CMD ["/start.sh"]
