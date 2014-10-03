FROM kollaglue/fedora-rdo-base
MAINTAINER James Labocki <jlabocki@redhat.com>

RUN yum install -y openstack-heat-api \
	openstack-heat-api-cfn \
	openstack-heat-common \
	openstack-heat-api-cloudwatch \
	openstack-utils \
	python-openstackclient \
	&& yum clean all

ADD ./start.sh /start.sh

CMD ["/start.sh"]
